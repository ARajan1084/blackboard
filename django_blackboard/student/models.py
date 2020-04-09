from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    student_id = models.CharField(max_length=7)
    id_picture = models.ImageField(upload_to='id_pictures')
    email_address = models.CharField(max_length=320, null=True)

    def __str__(self):
        return self.first_name+'_'+self.last_name+'_'+self.student_id


class StudentClasses(models.Model):
    student_id = models.CharField(max_length=7, primary_key=True)
    course_id = models.CharField(max_length=10)
    period = models.IntegerField()