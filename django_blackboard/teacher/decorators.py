import uuid
from .models import Teacher
from board.models import Class, ClassAssignments, Assignment
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def authentication_required(function):
    def wrapper(request, *args, **kwargs):
        user = request.user
        try:
            teacher = Teacher.objects.all().get(user=user)
        except:
            return redirect('teacher-login')
        if kwargs.get('class_id'):
            klass = Class.objects.all().get(id=uuid.UUID(kwargs.get('class_id')))
            if klass.teacher_id == str(teacher.id.hex):
                return function(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        elif kwargs.get('assignment_id'):
            assignment = Assignment.objects.all().get(id=uuid.UUID(kwargs.get('assignment_id')))
            class_assignments = ClassAssignments.objects.all().filter(str(assignment.id.hex))
            for class_assignment in class_assignments:
                klass = Class.objects.all().get(id=uuid.UUID(class_assignment.class_id))
                if klass.teacher_id == str(teacher.id.hex):
                    return function(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden()
        return function(request, *args, **kwargs)
    return wrapper
