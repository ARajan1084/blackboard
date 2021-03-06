import uuid
import decimal

from django.utils import timezone

from board.models import Category, Assignment, ClassAssignments, Class, Course, Discussion, ClassDiscussions
from teacher.models import Teacher
from .models import Submission, ClassEnrollment, Student
from .forms import ThreadReplyForm


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


def get_assignments(enrollment):
    assignment_refs = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
    assignments = []
    for assignment_ref in assignment_refs:
        assignments.append(Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id)))
    return assignments


def fetch_relevant(submissions):
    late = {}
    tests = {}
    due_tomorrow = {}
    due_in_three_days = {}
    due_in_a_week = {}
    for assignment, submission in list(submissions.items()):
        if assignment.due_date > timezone.now():
            class_ref = ClassAssignments.objects.all().get(assignment_id=str(assignment.id.hex))
            klass = Class.objects.all().get(id=uuid.UUID(class_ref.class_id))
            course = Course.objects.all().get(course_id=klass.course_id)
            category = Category.objects.all().get(id=uuid.UUID(assignment.category_id).hex)
            if ('Test' in category.category_name) or ('Quiz' in category.category_name):
                tests.update({(assignment, course): submissions.pop(assignment)})
            elif submission.score is None:
                due_date = assignment.due_date
                current_date = timezone.now()
                delta = due_date - current_date
                if delta.days <= 1:
                    due_tomorrow.update({(assignment, course): submissions.pop(assignment)})
                elif delta.days <= 3:
                    due_in_three_days.update({(assignment, course): submissions.pop(assignment)})
                elif delta.days <= 8:
                    due_in_a_week.update({(assignment, course): submissions.pop(assignment)})
        elif submission.score == 0:
            class_ref = ClassAssignments.objects.all().get(assignment_id=str(assignment.id.hex))
            klass = Class.objects.all().get(id=uuid.UUID(class_ref.class_id))
            course = Course.objects.all().get(course_id=klass.course_id)
            teacher = Teacher.objects.all().get(id=uuid.UUID(klass.teacher_id))
            late.update({(assignment, course, teacher): submissions.pop(assignment)})
        else:
            submissions.pop(assignment)

    upcoming = {
        'late': late,
        'tests': tests,
        'due_tomorrow': due_tomorrow,
        'due_in_three_days': due_in_three_days,
        'due_in_a_week': due_in_a_week
    }
    return upcoming


def get_student_submissions(enrollments):
    submissions = {}
    for enrollment in enrollments:
        assignment_refs = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
        for assignment_ref in assignment_refs:
            assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id).hex)
            submission = Submission.objects.all().get(assignment_id=str(assignment.id.hex),
                                                      enrollment_id=str(enrollment.id.hex))
            submissions.update({assignment: submission})
    return submissions


def get_enrollments(student):
    return ClassEnrollment.objects.all().filter(student_id=student.student_id)


def get_class_data(enrollments):
    class_data = []
    for enrollment in enrollments:
        klass = Class.objects.all().get(id=enrollment.class_id)
        course = Course.objects.all().get(course_id=klass.course_id)
        teacher = Teacher.objects.all().get(id=klass.teacher_id)
        assignment_refs = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
        class_assignments = []
        for assignment_ref in assignment_refs:
            assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id).hex)
            class_assignments.append(assignment)

        grade = calculate_grade(class_assignments, str(enrollment.id.hex), klass.weighted)
        class_data.append({
            'period': klass.period,
            'course_name': course.course_name,
            'teacher_name': teacher.first_name + ' ' + teacher.last_name,
            'teacher_email': teacher.email_address,
            'grade': grade,
            'enrollment_id': str(enrollment.id.hex)
        })
    class_data.sort(key=(lambda klass: klass['period']))
    return class_data


def calculate_workload(enrollments):
    est_completion_time = 0
    for enrollment in enrollments:
        assignment_refs = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
        for assignment_ref in assignment_refs:
            assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id))
            if assignment.est_completion_time_min:
                submission = Submission.objects.all().get(enrollment_id=str(enrollment.id.hex), assignment_id=str(assignment.id.hex))
                if (assignment.due_date > timezone.now()) and (not submission.complete):
                    time_until_due = assignment.due_date - timezone.now()
                    if time_until_due.days == 0:
                        est_completion_time += assignment.est_completion_time_min
                    else:
                        est_completion_time += int(assignment.est_completion_time_min * 1 / time_until_due.days)

    return est_completion_time


def calculate_grade(assignments, enrollment_id, weighted):
    categories = {}
    for assignment in assignments:
        category = Category.objects.all().get(id=uuid.UUID(assignment.category_id).hex)
        category_weight = category.category_weight
        points = assignment.points
        earned = Submission.objects.all().get(enrollment_id=enrollment_id, assignment_id=str(assignment.id.hex)).score
        if earned is not None:
            sub_score = categories.get(category)
            if sub_score is not None:
                sub_score[0] += earned
                sub_score[1] += points
            else:
                categories.update({category: [earned, points, category_weight]})

    category_breakdown = {}
    for category, values in categories.items():
        category_breakdown.update({category: (values[0] * 100/values[1], values[2])})

    if weighted:
        if not categories:
            return None
        overall_grade_percent = 0
        overall_grade_denominator = 0
        for category_score in categories.values():
            overall_grade_percent += decimal.Decimal(category_score[0] * 100 / category_score[1]) * category_score[2]
            overall_grade_denominator += category_score[2]
        overall_grade_percent = overall_grade_percent / overall_grade_denominator
        return letter_grade(overall_grade_percent/100), overall_grade_percent, category_breakdown
    else:
        if not assignments:
            return None
        total_score = [0, 0]
        for assignment in assignments:
            points = assignment.points
            earned = Submission.objects.all().get(enrollment_id=enrollment_id,
                                                  assignment_id=str(assignment.id.hex)).score
            if earned:
                total_score[0] += earned
                total_score[1] += points
        if total_score[1] == 0:
            return None
        else:
            overall_grade_percentage = decimal.Decimal(total_score[0] * 100 / total_score[1])
        return letter_grade(overall_grade_percentage/100), overall_grade_percentage, category_breakdown


def letter_grade(percent):
    if percent >= 0.9:
        return 'A'
    elif percent >= 0.8:
        return 'B'
    elif percent >= 0.7:
        return 'C'
    elif percent >= 0.6:
        return 'D'
    else:
        return 'F'
