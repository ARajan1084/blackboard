import csv
import uuid
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import UserLoginForm
from django.contrib.auth.decorators import login_required
from .models import Student, ClassEnrollment
from board.models import Course, Class, ClassAssignments, Assignment, Category, ClassCategories
from teacher.models import Teacher


@login_required()
def home(request):
    student = Student.objects.all().get(user=request.user)
    classes = ClassEnrollment.objects.all().filter(student_id=student.student_id)
    class_data = []
    for enrollment in classes:
        klass = Class.objects.all().get(class_id=enrollment.class_id)
        course = Course.objects.all().get(course_id=klass.course_id)
        teacher = Teacher.objects.all().get(teacher_id=klass.teacher_id)
        assignment_refs = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
        assignments = []
        for assignment_ref in assignment_refs:
            assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id).hex)
            assignments.append(assignment)
        print(assignments)
        class_data.append(
            [klass.period,
             course.course_name,
             teacher.first_name + ' ' + teacher.last_name,
             assignments]
        )
    context = {
        'class_data': class_data
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
                    messages.error(request, 'student not found. wrong portal?')
            else:
                messages.error(request, 'invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'student/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return login(request)
