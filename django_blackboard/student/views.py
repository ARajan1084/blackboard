import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone

from .forms import UserLoginForm, ThreadReplyForm, NewThreadForm
from .models import Student, ClassEnrollment, Submission
from board.models import Course, Class, ClassAssignments, Assignment, Category, ClassCategories, Schedule, Notification, \
    ClassDiscussions, Discussion
from .utils import calculate_grade, get_student_submissions, get_enrollments, get_class_data, \
    fetch_relevant, calculate_workload, get_assignments, fetch_full_thread, fetch_all_discussions, \
    fetch_class_discussions
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
    discussions = fetch_class_discussions(str(klass.id.hex))

    context = {
        'period': klass.period,
        'course': course,
        'enrollment_id': enrollment_id,
        'active': active,
        'discussions': discussions
    }
    return render(request, 'student/discussions.html', context)


def thread(request, enrollment_id, discussion_id):
    root = Discussion.objects.all().get(id=uuid.UUID(discussion_id))
    if request.method == 'POST':
        all_discussions = fetch_all_discussions(root, all_discussions=None)
        form = ThreadReplyForm(discussions=all_discussions, data=request.POST)
        if form.is_valid():
            discussions = {}
            for key, value in form.cleaned_data.items():
                if value:
                    key_split = key.split('_')
                    reply = discussions.get(key_split[0])
                    if not reply:
                        reply = Discussion(user=request.user, reply_to=key_split[0], is_root=False)
                    if key_split[1] == 'message':
                        reply.message = value
                    elif key_split[1] == 'media':
                        reply.attached_media = value
                    discussions.update({key_split[0]: reply})
            for disc_id, discussion in discussions.items():
                discussion.save()
            return redirect('student-thread', enrollment_id, discussion_id)

    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)
    course = Course.objects.all().get(course_id=klass.course_id)

    full_thread_w_form = fetch_full_thread(0, root, None, None)
    full_thread = full_thread_w_form[0]
    form = full_thread_w_form[1]

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
def new_thread(request, enrollment_id):
    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    klass = Class.objects.all().get(id=uuid.UUID(enrollment.class_id).hex)

    if request.method == 'POST':
        form = NewThreadForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            message = form.cleaned_data.get('message')
            media = form.cleaned_data.get('media')
            discussion = Discussion(is_root=True, title=title, message=message, user=request.user, attached_media=media)
            discussion.save()
            class_discussion = ClassDiscussions(class_id=str(klass.id.hex), discussion_id=str(discussion.id.hex))
            class_discussion.save()
        return redirect('student-class', enrollment_id=enrollment_id, element='discussions')

    course = Course.objects.all().get(course_id=klass.course_id)
    form = NewThreadForm()

    context = {
        'active': 'discussions',
        'enrollment_id': enrollment_id,
        'course': course,
        'period': klass.period,
        'form': form
    }
    return render(request, 'student/new_thread.html', context)


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
