from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='administration-home'),
    path('login/', views.login, name='administration-login'),
    path('add_a_student/', views.add_student, name='administration-add-student'),
    path('<str:file_path>', views.download_file, name='administration-download-file')
]
