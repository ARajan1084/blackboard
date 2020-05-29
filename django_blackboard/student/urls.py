from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='student-board'),
    path('login/', views.login, name='student-login'),
    path('logout/', views.logout, name='student-logout'),
    path('calendar/', views.student_calendar, name='student-calendar'),
    path('class/discussions/thread/<str:enrollment_id>/<str:discussion_id>', views.thread, name='student-thread'),
    path('class/<str:element>/<str:enrollment_id>', views.klass, name='student-class')
]
