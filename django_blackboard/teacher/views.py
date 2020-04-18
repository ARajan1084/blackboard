import uuid
from collections import OrderedDict
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm
from .models import Teacher
from board.models import Class, ClassAssignments, Course, Assignment
from student.models import ClassEnrollment, Student, Submission


@login_required(login_url='teacher-login')
def home(request):
    teacher = Teacher.objects.all().get(user=request.user)
    classes = Class.objects.all().filter(teacher_id=str(teacher.id.hex))
    class_data = []
    for klass in classes:
        course = Course.objects.all().get(course_id=klass.course_id)
        num_students = ClassEnrollment.objects.all().filter(class_id=str(klass.id.hex)).count()
        class_data.append(
            [klass.period,
             course.course_name,
             num_students,
             str(klass.id.hex)]
        )
    context = {
        'class_data': class_data
    }
    return render(request, 'teacher/home.html', context)


@login_required(login_url='teacher-login')
def gradesheet(request, class_id):
    klass = Class.objects.all().get(id=uuid.UUID(class_id).hex)
    course_name = Course.objects.all().get(course_id=klass.course_id).course_name
    period = klass.period;
    enrollments = ClassEnrollment.objects.all().filter(class_id=class_id)
    assignment_ids = ClassAssignments.objects.all().filter(class_id=class_id)
    assignments = []
    for assignment_id in assignment_ids:
        assignments.append(Assignment.objects.all().get(id=uuid.UUID(assignment_id.assignment_id).hex))
    data = OrderedDict({})
    for enrollment in enrollments:
        student_name = get_student_name(enrollment)
        for assignment in assignments:
            submission = Submission.objects.get(enrollment_id=str(enrollment.id.hex), assignment_id=str(assignment.id.hex))
            try:
                current = data[student_name]
                score = (assignment, submission)
                data[student_name] = current + (score,)
            except:
                data.update({student_name: ((assignment, submission),)})
    context = {
        'course_name': course_name,
        'period': period,
        'assignments': assignments,
        'data': data
    }
    return render(request, 'teacher/gradesheet.html', context)


def get_student_name(enrollment):
    student = Student.objects.all().get(student_id=enrollment.student_id)
    student_name = student.first_name + ' ' + student.last_name
    return student_name


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
                    teacher = Teacher.objects.all().get(user=user)
                    auth_login(request, user)
                    if next:
                        return redirect(next)
                    return redirect('teacher-board')
                except:
                    messages.error(request, 'teacher not found. wrong portal?')
            else:
                messages.error(request, 'invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'teacher/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return login(request)
