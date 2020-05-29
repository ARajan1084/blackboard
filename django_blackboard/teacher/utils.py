import uuid
from collections import OrderedDict

from student.models import Student, Submission
from board.models import ClassAssignments, Assignment, Category, ClassCategories, Discussion
from student.utils import calculate_grade


def fetch_full_thread(indent, root):
    full_thread = []
    replies = Discussion.objects.all().filter(reply_to=str(root.id.hex))
    for reply in replies:
        full_thread.append((indent, reply))
        replies_to_reply = Discussion.objects.all().filter(reply_to=str(reply.id.hex))
        for reply_to_reply in replies_to_reply:
            fetch_full_thread(indent+1, reply_to_reply)
    return full_thread


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
