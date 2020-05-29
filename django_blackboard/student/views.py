import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone

from .forms import UserLoginForm
from .models import Student, ClassEnrollment, Submission
from board.models import Course, Class, ClassAssignments, Assignment, Category, ClassCategories, Schedule, Notification, \
    ClassDiscussions, Discussion
from .utils import calculate_grade, get_student_submissions, get_enrollments, get_class_data, \
    fetch_relevant, calculate_workload, get_assignments, fetch_full_thread
from .decorators import authentication_required


def student_calendar(request):
    return render(request, 'student/calendar.html')


@authentication_required
def klass(request, element, enrollment_id):
    if element == 'grades':
        return grades(request, enrollment_id, active=element)
    elif element == 'dashboard':
        return dashboard(request, enrollment_id, active=element)
    elif element == 'resources':
        return resources(request, enrollment_id, active=element)
    elif element == 'discussions':
        return discussions(request, enrollment_id, active=element)


@authentication_required
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


@authentication_required
def dashboard(request, enrollment_id, active):
    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    assignments = get_assignments(enrollment)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)
    course = Course.objects.all().get(course_id=klass.course_id)
    period = klass.period
    submissions = get_student_submissions((enrollment,))

    upcoming = fetch_relevant(submissions)
    late = upcoming.get('late')
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
        'late': late,
        'due_tomorrow': due_tomorrow,
        'due_in_three_days': due_in_three_days,
        'due_in_a_week': due_in_a_week,
        'tests': tests,
        'est_completion_time': est_completion_time
    }
    return render(request, 'student/dashboard.html', context)


@authentication_required
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


@authentication_required
def discussions(request, enrollment_id, active):
    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)
    course = Course.objects.all().get(course_id=klass.course_id)
    period = klass.period

    discussion_refs = ClassDiscussions.objects.all().filter(class_id=str(klass.id.hex))
    discussions = []
    for discussion_ref in discussion_refs:
        discussion = Discussion.objects.all().get(id=uuid.UUID(discussion_ref.discussion_id))
        discussions.append(discussion)

    context = {
        'period': period,
        'course': course,
        'enrollment_id': enrollment_id,
        'active': active,
        'discussions': discussions
    }
    return render(request, 'student/discussions.html', context)


def thread(request, enrollment_id, discussion_id):
    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)
    course = Course.objects.all().get(course_id=klass.course_id)

    root = Discussion.objects.all().get(id=uuid.UUID(discussion_id))
    full_thread_w_form = fetch_full_thread(0, root)
    full_thread = full_thread_w_form[0]
    form = full_thread_w_form[1]
    print(full_thread_w_form)

    context = {
        'active': 'discussions',
        'enrollment_id': enrollment_id,
        'course': course,
        'period': klass.period,
        'root': root,
        'full_thread': full_thread,
        'form': form
    }
    return render(request, 'student/thread.html', context)


@authentication_required
def home(request):
    notifications = Notification.objects.all().filter(recipient=request.user)
    student = Student.objects.all().get(user=request.user)
    enrollments = get_enrollments(student)

    submissions = get_student_submissions(enrollments)
    class_data = get_class_data(enrollments)

    relevant = fetch_relevant(submissions)
    late = relevant.get('late')
    tests = relevant.get('tests')
    due_tomorrow = relevant.get('due_tomorrow')
    due_in_three_days = relevant.get('due_in_three_days')
    due_in_a_week = relevant.get('due_in_a_week')
    est_completion_time = calculate_workload(enrollments)

    class_workloads = {}
    for enrollment in enrollments:
        klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id))
        course = Course.objects.all().get(course_id=klass.course_id)
        class_workloads.update({course: calculate_workload((enrollment, ))})

    context = {
        'student': student,
        'request': request,
        'notifications': notifications,
        'class_data': class_data,
        'late': late,
        'due_tomorrow': due_tomorrow,
        'due_in_three_days': due_in_three_days,
        'due_in_a_week': due_in_a_week,
        'tests': tests,
        'est_completion_time': est_completion_time,
        'class_workloads': class_workloads
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
