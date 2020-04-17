from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone


class Course(models.Model):
    course_id = models.CharField(max_length=8, primary_key=True)
    course_name = models.CharField(max_length=25)

    def __str__(self):
        return self.course_name + '_' + self.course_id

    class Meta:
        db_table = 'courses'
        order_with_respect_to = 'course_id'


class Class(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    course_id = models.CharField(max_length=8, unique=False)
    teacher_id = models.CharField(max_length=100, unique=False)
    period = models.IntegerField()
    weighted = models.BooleanField(unique=False, default=False)

    def __str__(self):
        return self.course_id + '_' + self.teacher_id

    class Meta:
        db_table = 'classes'


class ClassAssignments(models.Model):
    class_id = models.CharField(max_length=100, unique=False)
    assignment_id = models.CharField(max_length=100, unique=False)

    def __str__(self):
        return self.class_id + '_' + self.assignment_id

    class Meta:
        db_table = 'class_assignments'


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    assignment_name = models.CharField(max_length=80, unique=False)
    category_id = models.CharField(max_length=100, unique=False)
    assignment_description = models.CharField(max_length=150, unique=False, null=True)
    points = models.IntegerField()
    created = models.DateTimeField(null=True, auto_now=True)
    updated = models.DateTimeField(null=True)
    assigned = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)

    def assign(self, due_date):
        if self.assigned is None:
            self.assigned = timezone.now()
        self.updated = timezone.now()
        self.due_date = due_date

    def __str__(self):
        return self.assignment_name

    class Meta:
        db_table = 'assignments'
        order_with_respect_to = 'id'


class ClassCategories(models.Model):
    class_id = models.CharField(max_length=100, unique=False)
    category_id = models.CharField(max_length=100, unique=False)

    def __str__(self):
        return self.class_id + '_' + self.category_id

    class Meta:
        db_table = 'class_categories'


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    category_name = models.CharField(max_length=25, unique=False)
    category_description = models.CharField(max_length=150, unique=False, null=True, default=None)
    category_weight = models.DecimalField(decimal_places=3, max_digits=3, null=True)

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = 'categories'
