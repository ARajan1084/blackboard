import uuid

from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from .models import Student, ClassEnrollment


def authentication_required(function):
    def wrapper(request, *args, **kwargs):
        user = request.user
        try:
            student = Student.objects.all().get(user=user)
        except:
            return redirect('student-logout')
        if kwargs.get('enrollment_id'):
            enrollment = ClassEnrollment.objects.get(id=uuid.UUID(kwargs.get('enrollment_id')))
            if student.student_id == enrollment.student_id:
                return function(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        return function(request, *args, **kwargs)
    return wrapper