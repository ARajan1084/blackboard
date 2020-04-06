from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='board-home'),
    path('student/', include('student.urls'), name='student-board'),
    path('teacher/', include('teacher.urls'), name='teacher-board')
]
