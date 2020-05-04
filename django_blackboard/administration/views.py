from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, CreateStudentForm, UploadCSVForm
from .models import Administrator
import mimetypes


@login_required(login_url='administration-login')
def home(request):
    return render(request, 'administration/home.html')


def add_student(request):
    create_form = CreateStudentForm()
    upload_form = UploadCSVForm()
    context = {
        'create_form': create_form,
        'upload_form': upload_form
    }
    return render(request, 'administration/add_student.html', context)


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