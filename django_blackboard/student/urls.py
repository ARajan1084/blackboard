from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='student-board'),
    path('login/', views.login, name='student-login'),
    path('logout/', views.logout, name='student-logout'),
    path('class/<str:element>/<str:enrollment_id>', views.klass, name='student-class')
]
