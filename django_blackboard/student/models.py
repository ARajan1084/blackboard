from django.db import models
from django.contrib.auth.models import User
import uuid


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    student_id = models.CharField(max_length=7, primary_key=True)
    grade = models.IntegerField(unique=False, default=11)
    id_picture = models.ImageField(upload_to='media/id_pictures')
    email_address = models.CharField(max_length=320, null=True)

    def __str__(self):
        return self.first_name+'_'+self.last_name+'_'+self.student_id

    class Meta:
        db_table = 'students'
        order_with_respect_to = 'student_id'


class ClassEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    student_id = models.CharField(max_length=7, unique=False)
    class_id = models.CharField(max_length=100, unique=False)

    def __str__(self):
        return self.student_id + '_' + self.class_id

    class Meta:
        db_table = 'class_enrollment'
        order_with_respect_to = 'student_id'


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    assignment_id = models.CharField(max_length=100, unique=False)
    enrollment_id = models.CharField(max_length=100, unique=False)
    date_submitted = models.DateTimeField(null=True, default=None)
    score = models.IntegerField(unique=False, null=True, default=None)
    file = models.FileField(upload_to='media/submission_files', null=True, default=None, unique=False)
    comments = models.CharField(max_length=200, null=True, default=None, unique=False)

    def __str__(self):
        return self.enrollment_id + '_' + self.assignment_id

    class Meta:
        db_table = 'submissions'
        order_with_respect_to = 'assignment_id'
