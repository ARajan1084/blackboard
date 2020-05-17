import uuid
import decimal

from django.utils import timezone

from board.models import Category, Assignment, ClassAssignments, Class, Course
from teacher.models import Teacher
from .models import Submission, ClassEnrollment


def get_assignments(enrollment):
    assignment_refs = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
    assignments = []
    for assignment_ref in assignment_refs:
        assignments.append(Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id)))
    return assignments


def fetch_upcoming(submissions):
    tests = {}
    for assignment, submission in list(submissions.items()):
        if assignment.due_date > timezone.now():
            category = Category.objects.all().get(id=uuid.UUID(assignment.category_id).hex)
            if ('Test' in category.category_name) or ('Quiz' in category.category_name):
                tests.update({assignment: submissions.pop(assignment)})
        else:
            submissions.pop(assignment)

    due_tomorrow = {}
    due_in_three_days = {}
    due_in_a_week = {}
    for assignment, submission in list(submissions.items()):
        if submission.score is None:
            due_date = assignment.due_date
            current_date = timezone.now()
            delta = due_date - current_date
            if delta.days <= 1:
                due_tomorrow.update({assignment: submissions.pop(assignment)})
            elif delta.days <= 3:
                due_in_three_days.update({assignment: submissions.pop(assignment)})
            elif delta.days <= 8:
                due_in_a_week.update({assignment: submissions.pop(assignment)})
    upcoming = {
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
        class_data.append(
            [klass.period,
             course.course_name,
             teacher.first_name + ' ' + teacher.last_name,
             grade,
             [],
             str(enrollment.id).replace('-', '')]
        )
    class_data.sort(key=(lambda a: a[0]))
    return class_data


def calculate_workload(enrollments):
    est_completion_time = 0
    for enrollment in enrollments:
        assignment_refs = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
        for assignment_ref in assignment_refs:
            assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id))
            submission = Submission.objects.all().get(enrollment_id=str(enrollment.id.hex), assignment_id=str(assignment.id.hex))
            if (assignment.due_date > timezone.now()) and (not submission.complete):
                est_completion_time += assignment.est_completion_time_min
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
            total_score[0] += earned
            total_score[1] += points
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
