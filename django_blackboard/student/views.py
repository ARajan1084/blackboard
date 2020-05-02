import csv
import decimal
import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone

from .forms import UserLoginForm
from django.contrib.auth.decorators import login_required
from .models import Student, ClassEnrollment, Submission
from board.models import Course, Class, ClassAssignments, Assignment, Category, ClassCategories, Schedule
from teacher.models import Teacher


def klass(request, element, enrollment_id):
    if element == 'grades':
        return grades(request, enrollment_id, active=element)
    elif element == 'dashboard':
        return dashboard(request, enrollment_id, active=element)
    elif element == 'resources':
        return resources(request, enrollment_id, active=element)
    elif element == 'discussions':
        return discussions(request, enrollment_id, active=element)


@login_required()
def grades(request, enrollment_id, active):
    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)
    course = Course.objects.all().get(course_id=klass.course_id)
    period = klass.period
    assignment_ids = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
    assignments = {}
    for assignment_ref in assignment_ids:
        assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id).hex)
        category_name = Category.objects.all().get(id=uuid.UUID(assignment.category_id).hex)
        submission = Submission.objects.all().get(enrollment_id=enrollment_id,
                                                  assignment_id=assignment_ref.assignment_id)
        assignments.update({assignment: (category_name, submission)})
    grades = calculate_grade(assignments.keys())
    context = {
        'active': active,
        'enrollment_id': enrollment_id,
        'period': period,
        'course': course,
        'assignments': assignments,
        'grades': grades
    }
    return render(request, 'student/grades.html', context)


@login_required()
def dashboard(request, enrollment_id, active):
    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)
    course = Course.objects.all().get(course_id=klass.course_id)
    period = klass.period
    context = {
        'period': period,
        'course': course,
        'enrollment_id': enrollment_id,
        'active': active
    }
    return render(request, 'student/dashboard.html', context)


@login_required()
def resources(request, enrollment_id, active):
    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)
    course = Course.objects.all().get(course_id=klass.course_id)
    period = klass.period
    context = {
        'period': period,
        'course': course,
        'enrollment_id': enrollment_id,
        'active': active
    }
    return render(request, 'student/resources.html', context)


@login_required()
def discussions(request, enrollment_id, active):
    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)
    course = Course.objects.all().get(course_id=klass.course_id)
    period = klass.period
    context = {
        'period': period,
        'course': course,
        'enrollment_id': enrollment_id,
        'active': active
    }
    return render(request, 'student/discussions.html', context)


@login_required()
def home(request):
    student = Student.objects.all().get(user=request.user)
    classes = ClassEnrollment.objects.all().filter(student_id=student.student_id)

    day_of_week = day_index_to_weekday(timezone.now().date().weekday())
    schedule = Schedule.objects.all().filter(day=day_of_week)

    submissions = {}
    class_data = []
    for enrollment in classes:
        klass = Class.objects.all().get(id=enrollment.class_id)
        course = Course.objects.all().get(course_id=klass.course_id)
        teacher = Teacher.objects.all().get(id=klass.teacher_id)
        assignment_refs = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
        class_assignments = []
        for assignment_ref in assignment_refs:
            assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id).hex)
            submission = Submission.objects.all().get(assignment_id=str(assignment.id).replace('-', ''),
                                                      enrollment_id=str(enrollment.id).replace('-', ''))
            submissions.update({assignment: submission})
            class_assignments.append(assignment)
        grade = calculate_grade(class_assignments)
        class_data.append(
            [klass.period,
             course.course_name,
             teacher.first_name + ' ' + teacher.last_name,
             grade,
             [],
             str(enrollment.id).replace('-', '')]
        )

    tests = fetch_upcoming_tests(submissions)
    due_tomorrow = {}
    due_in_three_days = {}
    due_in_a_week = {}

    for assignment, submission in list(submissions.items()):
        due_date = assignment.due_date
        current_date = timezone.now()
        if due_date > current_date and submission.score is None:
            delta = due_date - current_date
            if delta.days <= 1:
                due_tomorrow.update({assignment: submissions.pop(assignment)})
            elif delta.days <= 3:
                due_in_three_days.update({assignment: submissions.pop(assignment)})
            elif delta.days <= 8:
                due_in_a_week.update({assignment: submissions.pop(assignment)})

    context = {
        'class_data': class_data,
        'due_tomorrow': due_tomorrow,
        'due_in_three_days': due_in_three_days,
        'due_in_a_week': due_in_a_week,
        'tests': tests
    }
    return render(request, 'student/home.html', context)


def fetch_upcoming_tests(submissions):
    tests = {}
    for assignment, submission in list(submissions.items()):
        if assignment.due_date > timezone.now():
            category = Category.objects.all().get(id=uuid.UUID(assignment.category_id).hex)
            if (category.category_name == 'Tests'
                    or category.category_name == 'Tests/Quizzes'
                    or category.category_name == 'Quizzes'):
                tests.update({assignment: submissions.pop(assignment)})
        else:
            submissions.pop(assignment)
    return tests


def day_index_to_weekday(index):
    weekdays = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    return weekdays[index]


def calculate_grade(assignments):
    categories = {}
    for assignment in assignments:
        category = Category.objects.all().get(id=uuid.UUID(assignment.category_id).hex)
        category_name = category.category_name
        category_weight = category.category_weight
        points = assignment.points
        earned = Submission.objects.all().get(assignment_id=str(assignment.id.hex)).score
        if earned is not None:
            sub_score = categories.get(category_name)
            if sub_score is not None:
                sub_score[0] += earned
                sub_score[1] += points
            else:
                categories.update({category_name: [earned, points, category_weight]})
    overall_grade_percent = 0
    category_breakdown = {}
    for category_name, values in categories.items():
        category_breakdown.update({category_name: values[0] * 100/values[1]})
    for category_score in categories.values():
        overall_grade_percent += decimal.Decimal(category_score[0] * 100 / category_score[1]) * category_score[2]
    return letter_grade(overall_grade_percent), overall_grade_percent, category_breakdown


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


def login(request):
    next = request.GET.get('next')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                try:
                    student = Student.objects.all().get(user=user)
                    auth_login(request, user)
                    if next:
                        return redirect(next)
                    return redirect('student-board')
                except:
                    messages.error(request, 'student not found. wrong portal?')
            else:
                messages.error(request, 'invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'student/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return login(request)
