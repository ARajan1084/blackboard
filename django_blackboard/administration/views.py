import pickle
import traceback
from django.db.utils import IntegrityError
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, CreateStudentForm, UploadCSVForm
from .models import Administrator
from student.models import Student
from django.contrib.auth.models import User
import mimetypes
import pandas as pd


@login_required(login_url='administration-login')
def home(request):
    return render(request, 'administration/home.html')


def add_student(request):
    if request.method == 'POST':
        if 'confirm_upload' in request.POST:
            users = request.session.get('users')
            students = serializers.deserialize('json', request.session.get('students'))
            num_students_added = 0
            for user_info, student in zip(users, list(student.object for student in students)):
                user = User.objects.get_or_create(username=user_info[0], password=user_info[1])[0]
                student.user = user
                try:
                    student.save(student_id=student.student_id)
                    num_students_added += 1
                except IntegrityError:
                    pass
                else:
                    traceback.print_exc()
                    messages.error(request, 'Something went horribly wrong. Please try again later.')
                    break
            messages.success(request, message=(str(num_students_added) + ' students added successfully!'))
        if 'upload' in request.POST:
            upload_form = UploadCSVForm(request.POST, request.FILES)
            if upload_form.is_valid():
                csv = upload_form.cleaned_data.get('csv')
                df = pd.read_csv(csv, header=0, dtype=str)
                try:
                    users = []
                    students = []
                    for index, row in df.iterrows():
                        user_info = (row['username'], row['password'])
                        student = Student(user=None,
                                          first_name=row['first_name'],
                                          last_name=row['last_name'],
                                          email_address=row['email_address'],
                                          student_id=row['student_id'],
                                          grade=int(row['grade']))
                        users.append(user_info)
                        students.append(student)
                    request.session['users'] = users
                    request.session['students'] = serializers.serialize('json', students)
                    return confirm_student_uploads(request, users, students)
                except:
                    traceback.print_exc()
                    messages.error(request, 'Errors exist in the formatting of the uploaded CSV.')

    create_form = CreateStudentForm()
    upload_form = UploadCSVForm()
    context = {
        'create_form': create_form,
        'upload_form': upload_form
    }
    return render(request, 'administration/add_student.html', context)


def confirm_student_uploads(request, users, students):
    context = {
        'students': list(zip(users, students))
    }
    return render(request, 'administration/confirm_student_upload.html', context)


def download_file(request, file_path):
    file_path = file_path.replace('-', '/')
    file_name = 'content.extension'
    mime_type = mimetypes.guess_type(file_path)

    file = open(file_path, 'r')
    response = HttpResponse(file, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % file_name
    return response


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
                    admin = Administrator.objects.all().get(user=user)
                    auth_login(request, user)
                    if next:
                        return redirect(next)
                    return redirect('administration-home')
                except:
                    messages.error(request, 'Administrator not found. Wrong portal?')
            else:
                messages.error(request, 'Invalid username or password')

    form = UserLoginForm()
    return render(request, 'administration/login.html', {'form': form})
