from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='teacher-board'),
    path('login/', views.login, name='teacher-login'),
    path('logout/', views.logout, name='teacher-logout'),
    path('gradesheet/<class_id>', views.gradesheet, name='teacher-gradesheet')
]
