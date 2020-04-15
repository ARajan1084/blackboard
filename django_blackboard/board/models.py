from django.db import models
from django.contrib.auth.models import User
import uuid


class Course(models.Model):
    course_id = models.CharField(max_length=8, primary_key=True)
    course_name = models.CharField(max_length=25)

    def __str__(self):
        return self.course_name + '_' + self.course_id

    class Meta:
        db_table = 'courses'
        order_with_respect_to = 'course_id'


class Class(models.Model):
    class_id = models.CharField(max_length=20, primary_key=True)
    course_id = models.CharField(max_length=8, unique=False)
    teacher_id = models.CharField(max_length=4, unique=False)
    period = models.IntegerField()
    weighted = models.BooleanField(unique=False, default=False)

    def __str__(self):
        return self.class_id

    class Meta:
        db_table = 'classes'
        order_with_respect_to = 'class_id'


class ClassAssignments(models.Model):
    class_id = models.CharField(max_length=20, unique=False)
    assignment_id = models.CharField(max_length=100, unique=False)

    def __str__(self):
        return self.class_id + '_' + self.assignment_id

    class Meta:
        db_table = 'class_assignments'
        order_with_respect_to = 'class_id'


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False, unique=True)
    assignment_name = models.CharField(max_length=80, unique=False)
    category_id = models.CharField(max_length=100, unique=False)
    assignment_description = models.CharField(max_length=150, unique=False, null=True)
    points = models.IntegerField()

    def __str__(self):
        return self.assignment_name

    class Meta:
        db_table = 'assignments'
        order_with_respect_to = 'id'


class ClassCategories(models.Model):
    class_id = models.CharField(max_length=20, unique=False)
    category_id = models.CharField(max_length=20, unique=False)

    def __str__(self):
        return self.class_id + '_' + self.category_id

    class Meta:
        db_table = 'class_categories'
        order_with_respect_to = 'class_id'


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    category_name = models.CharField(max_length=25, unique=False)
    category_description = models.CharField(max_length=150, unique=False, null=True, default=None)
    category_weight = models.DecimalField(decimal_places=3, max_digits=3, null=True)

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = 'categories'
        order_with_respect_to = 'id'
