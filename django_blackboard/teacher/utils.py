import uuid
from collections import OrderedDict

from student.models import Student, Submission, ClassEnrollment
from board.models import ClassAssignments, Assignment, Category, ClassCategories, Discussion, ClassDiscussions, Class
from student.utils import calculate_grade
from teacher.models import Teacher

from .forms import ThreadReplyForm


def get_student_scores(assignment_id):
    class_assignment = ClassAssignments.objects.all().get(assignment_id=assignment_id)
    klass = Class.objects.all().get(id=uuid.UUID(class_assignment.class_id).hex)
    class_enrollments = ClassEnrollment.objects.all().filter(class_id=str(klass.id).replace('-', ''))
    student_scores = []
    for enrollment in class_enrollments:
        student = Student.objects.all().get(student_id=enrollment.student_id)
        submission_score = Submission.objects.all().get(enrollment_id=str(enrollment.id).replace('-', ''),
                                                        assignment_id=assignment_id).score
        student_scores.append((student, submission_score))
    return student_scores


def get_submissions(class_id, assignment_id):
    class_enrollments = ClassEnrollment.objects.all().filter(class_id=class_id)
    submissions = []
    for enrollment in class_enrollments:
        submission = Submission.objects.all().get(enrollment_id=str(enrollment.id).replace('-', ''),
                                                  assignment_id=assignment_id)
        submissions.append(submission)
    return submissions


def fetch_class_discussions(class_id):
    discussion_refs = ClassDiscussions.objects.all().filter(class_id=class_id)
    discussions = []
    for discussion_ref in discussion_refs:
        discussion = Discussion.objects.all().get(id=uuid.UUID(discussion_ref.discussion_id))
        name = fetch_name(discussion.user)
        discussions.append((name, discussion))
    discussions.sort(reverse=True, key=lambda i: i[1].date_posted)
    return discussions


def fetch_full_thread(indent, root, full_thread, all_discussions):
    if not all_discussions:
        all_discussions = [root]
    else:
        all_discussions.append(root)
    if not full_thread:
        full_thread = [(indent, (root, fetch_name(root.user)))]
    else:
        full_thread.append((indent, (root, fetch_name(root.user))))
    replies = Discussion.objects.all().filter(reply_to=str(root.id.hex))
    for reply in replies:
        fetch_full_thread(indent + 50, reply, full_thread, all_discussions)
    return full_thread, ThreadReplyForm(discussions=all_discussions)


def fetch_all_discussions(root, all_discussions):
    if not all_discussions:
        all_discussions = [root]
    else:
        all_discussions.append(root)
    replies = Discussion.objects.all().filter(reply_to=str(root.id.hex))
    for reply in replies:
        fetch_all_discussions(reply, all_discussions)
    return all_discussions


def fetch_name(user):
    try:
        student = Student.objects.all().get(user=user)
        return student.first_name + ' ' + student.last_name
    except:
        pass
    try:
        teacher = Teacher.objects.all().get(user=user)
        return teacher.first_name + ' ' + teacher.last_name
    except:
        pass
    return None



def fetch_category_breakdown(klass, enrollments):
    category_breakdown = {}
    category_refs = ClassCategories.objects.all().filter(class_id=str(klass.id.hex))
    for category_ref in category_refs:
        category = Category.objects.all().get(id=uuid.UUID(category_ref.category_id))
        category_breakdown.update({category: []})
    for enrollment in enrollments:
        assignments = fetch_assignments(str(klass.id.hex))
        grades = calculate_grade(assignments=assignments, enrollment_id=str(enrollment.id.hex), weighted=klass.weighted)
        if grades:
            for category, values in grades[2].items():
                scores = category_breakdown.get(category)
                scores.append(values[0])
    return category_breakdown


def fetch_raw_grades(grades):
    raw_grades = []
    for student, grade in grades.items():
        if grade:
            raw_grades.append(float(grade[1]))
    return raw_grades


def fetch_assignments(class_id):
    assignment_refs = ClassAssignments.objects.all().filter(class_id=class_id)
    assignments = []
    for assignment_ref in assignment_refs:
        assignments.append(Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id)))
    return assignments


def fetch_assignments_with_categories(class_id):
    assignment_ids = ClassAssignments.objects.all().filter(class_id=class_id)
    assignments = []
    for assignment_id in assignment_ids:
        assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_id.assignment_id).hex)
        category = Category.objects.all().get(id=uuid.UUID(assignment.category_id))
        assignments.append((assignment, category))
    return assignments


def fetch_gradesheet_data(klass, enrollments, assignments):
    data = OrderedDict({})
    grades = {}
    for enrollment in enrollments:
        student = Student.objects.all().get(student_id=enrollment.student_id)
        grades.update({student: calculate_grade(assignments=[assignment[0] for assignment in assignments],
                                                enrollment_id=str(enrollment.id.hex),
                                                weighted=klass.weighted)})
        for assignment, category in assignments:
            submission = Submission.objects.get(enrollment_id=str(enrollment.id.hex),
                                                assignment_id=str(assignment.id.hex))
            try:
                current = data[student]
                score = (assignment, submission)
                data[student] = current + (score,)
            except:
                data.update({student: ((assignment, submission),)})
    # data = sorted(data.items(), key=lambda tup: tup[0].first_name)
    # print(data)

    gradesheet_data = {
        'grades': grades,
        'data': data
    }
    return gradesheet_data
