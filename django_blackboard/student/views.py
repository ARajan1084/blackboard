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
from .utils import calculate_grade, get_student_submissions, get_enrollments, get_class_data, \
    fetch_upcoming, calculate_workload, get_assignments


def student_calendar(request):
    return render(request, 'student/calendar.html')


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
        if assignment.due_date < timezone.now():
            category_name = Category.objects.all().get(id=uuid.UUID(assignment.category_id).hex)
            submission = Submission.objects.all().get(enrollment_id=enrollment_id,
                                                      assignment_id=assignment_ref.assignment_id)
            assignments.update({assignment: (category_name, submission)})
        else:
            print(assignment)

    grades = calculate_grade(assignments.keys(), enrollment_id, klass.weighted)
    context = {
        'active': active,
        'weighted': klass.weighted,
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
    assignments = get_assignments(enrollment)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)
    course = Course.objects.all().get(course_id=klass.course_id)
    period = klass.period
    submissions = get_student_submissions((enrollment,))

    upcoming = fetch_upcoming(submissions)
    tests = upcoming.get('tests')
    due_tomorrow = upcoming.get('due_tomorrow')
    due_in_three_days = upcoming.get('due_in_three_days')
    due_in_a_week = upcoming.get('due_in_a_week')
    est_completion_time = calculate_workload((enrollment,))

    context = {
        'period': period,
        'course': course,
        'enrollment_id': enrollment_id,
        'active': active,
        'due_tomorrow': due_tomorrow,
        'due_in_three_days': due_in_three_days,
        'due_in_a_week': due_in_a_week,
        'tests': tests,
        'est_completion_time': est_completion_time
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
    enrollments = get_enrollments(student)

    submissions = get_student_submissions(enrollments)
    class_data = get_class_data(enrollments)

    upcoming = fetch_upcoming(submissions)
    tests = upcoming.get('tests')
    due_tomorrow = upcoming.get('due_tomorrow')
    due_in_three_days = upcoming.get('due_in_three_days')
    due_in_a_week = upcoming.get('due_in_a_week')
    est_completion_time = calculate_workload(enrollments)

    context = {
        'class_data': class_data,
        'due_tomorrow': due_tomorrow,
        'due_in_three_days': due_in_three_days,
        'due_in_a_week': due_in_a_week,
        'tests': tests,
        'est_completion_time': est_completion_time
    }
    return render(request, 'student/home.html', context)


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
                    messages.error(request, 'Student not found. Wrong portal?')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'student/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return login(request)
