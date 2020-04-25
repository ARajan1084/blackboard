import csv
import decimal
import uuid
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import UserLoginForm
from django.contrib.auth.decorators import login_required
from .models import Student, ClassEnrollment, Submission
from board.models import Course, Class, ClassAssignments, Assignment, Category, ClassCategories
from teacher.models import Teacher


@login_required()
def klass(request, enrollment_id):
    enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(enrollment_id).hex)
    assignment_ids = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
    assignments = {}
    for assignment_ref in assignment_ids:
        assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id).hex)
        submission = Submission.objects.all().get(enrollment_id=enrollment_id,
                                                  assignment_id=assignment_ref.assignment_id)
        assignments.update({assignment: submission})
    context = {
        'assignments': assignments
    }
    return render(request, 'student/class.html', context)


@login_required()
def home(request):
    student = Student.objects.all().get(user=request.user)
    classes = ClassEnrollment.objects.all().filter(student_id=student.student_id)
    class_data = []
    for enrollment in classes:
        klass = Class.objects.all().get(id=enrollment.class_id)
        course = Course.objects.all().get(course_id=klass.course_id)
        teacher = Teacher.objects.all().get(id=klass.teacher_id)
        assignment_refs = ClassAssignments.objects.all().filter(class_id=enrollment.class_id)
        assignments = []
        for assignment_ref in assignment_refs:
            assignment = Assignment.objects.all().get(id=uuid.UUID(assignment_ref.assignment_id).hex)
            assignments.append(assignment)
        grade = calculate_grade(assignments)
        class_data.append(
            [klass.period,
             course.course_name,
             teacher.first_name + ' ' + teacher.last_name,
             grade,
             assignments,
             str(enrollment.id).replace('-', '')]
        )
    context = {
        'class_data': class_data
    }
    return render(request, 'student/home.html', context)


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
                categories.update({category_name: (earned, points, category_weight)})
    overall_grade_percent = 0
    for category_score in categories.values():
        overall_grade_percent += decimal.Decimal(category_score[0] * 100 / category_score[1]) * category_score[2]
    return letter_grade(overall_grade_percent), overall_grade_percent


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
