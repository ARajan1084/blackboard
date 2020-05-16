import uuid
from collections import OrderedDict

from student.models import Student, Submission
from board.models import ClassAssignments, Assignment, Category
from student.utils import calculate_grade


def fetch_raw_grades(grades):
    raw_grades = []
    for student, grade in grades.items():
        raw_grades.append(float(grade[1]))
    return raw_grades


def fetch_assignments(class_id):
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
    gradesheet_data = {
        'grades': grades,
        'data': data
    }
    return gradesheet_data
