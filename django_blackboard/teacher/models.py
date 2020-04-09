from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    teacher_id = models.CharField(max_length=4)
    id_picture = models.ImageField(upload_to='id_pictures')
    email_address = models.CharField(max_length=320)

    def __str__(self):
        return self.first_name+'_'+self.last_name


class TeacherClasses(models.Model):
    teacher_id = models.CharField(max_length=7, primary_key=True)
    course_id = models.CharField(max_length=10)
    period = models.IntegerField()
