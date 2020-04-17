from django.contrib import admin
from .models import Student, ClassEnrollment, Submission


admin.site.register(Student)
admin.site.register(ClassEnrollment)
admin.site.register(Submission)
