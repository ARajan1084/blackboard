from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='teacher-board'),
    path('login/', views.login, name='teacher-login'),
    path('logout/', views.logout, name='teacher-logout'),
    path('class/<str:element>/<str:class_id>', views.klass, name='teacher-class'),
    path('class/discussions/thread/<str:class_id>/<str:discussion_id>', views.thread, name='teacher-discussion'),
    path('class/discussions/new/<str:class_id>', views.new_thread, name='teacher-new-thread'),
    path('new_assignment/<str:class_id>', views.new_assignment, name='teacher-new-assignment'),
    path('new_category/<str:class_id>/<str:edit>', views.new_category, name='teacher-new-category'),
    path('assignment/<str:class_id>/<str:assignment_id>/<str:edit>', views.assignment, name='teacher-assignment')
]
