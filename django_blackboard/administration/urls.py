from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='administration-home'),
    path('login/', views.login, name='administration-login'),
    path('add_student/', views.add_student, name='administration-add-student'),
    path('add_teacher', views.add_teacher, name='administration-add-teacher'),
    path('<str:file_path>', views.download_file, name='administration-download-file')
]
