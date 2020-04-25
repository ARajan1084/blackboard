from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='teacher-board'),
    path('login/', views.login, name='teacher-login'),
    path('logout/', views.logout, name='teacher-logout'),
    path('gradesheet/<class_id>', views.gradesheet, name='teacher-gradesheet'),
    path('new_assignment/<class_id>', views.new_assignment, name='teacher-new-assignment'),
    path('assignment/<str:assignment_id>/<str:edit>', views.assignment, name='teacher-assignment')
]
