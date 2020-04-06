from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .forms import UserLoginForm
from django.contrib.auth.decorators import login_required
from .models import Student


@login_required()
def home(request):
    return render(request, 'student/home.html')


def login(request):
    next = request.GET.get('next')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                auth_login(request, user)
                student = Student.objects.get(user)
                if next:
                    return redirect(next)
                return redirect('student-board')
            else:
                messages.error(request, 'invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'student/login.html', {'form': form})
