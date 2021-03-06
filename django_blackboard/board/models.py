import os
import uuid
import shutil
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_blackboard.settings import MEDIA_ROOT


class Discussion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    is_root = models.BooleanField()
    title = models.CharField(max_length=100, unique=False, null=True)
    message = models.TextField(max_length=200, unique=False)
    attached_media = models.FileField(null=True, unique=False, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    reply_to = models.CharField(max_length=36, null=True, unique=False)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id.hex) + '_' + str(self.reply_to)

    class Meta:
        db_table = 'discussions'


class ClassDiscussions(models.Model):
    class_id = models.CharField(max_length=36, unique=False)
    discussion_id = models.CharField(max_length=36)

    def __str__(self):
        return self.class_id + '_' + self.discussion_id


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=150, unique=False)
    sent_date = models.DateTimeField(auto_now_add=True)
    link = models.TextField(max_length=200, null=True)
    read = models.BooleanField(null=True, default=False)

    def __str__(self):
        return str(self.recipient) + '_' + self.message + '_' + self.link

    class Meta:
        db_table = 'notifications'
        order_with_respect_to = 'recipient'


class Schedule(models.Model):
    period = models.CharField(unique=False, max_length=8)
    day = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.period + '_' + str(self.day) + '_' + str(self.start_time) + '_' + str(self.end_time)

    class Meta:
        db_table = 'schedules'
        order_with_respect_to = 'day'


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

    def save(self, *args, **kwargs):
        if self._state.adding:
            os.mkdir(os.path.join(MEDIA_ROOT + '/resources', str(self.id.hex)))
            os.mkdir(os.path.join(MEDIA_ROOT + '/submission_files', str(self.id.hex)))
            os.mkdir(os.path.join(MEDIA_ROOT + '/assignment_media', str(self.id.hex)))
        super(Class, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        shutil.rmtree(os.path.join(MEDIA_ROOT + '/resources', str(self.id.hex)))
        shutil.rmtree(os.path.join(MEDIA_ROOT + '/submission_files', str(self.id.hex)))
        shutil.rmtree(os.path.join(MEDIA_ROOT + '/assignment_media', str(self.id.hex)))
        super(Class, self).delete(*args, **kwargs)

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


def generate_assignment_media_file_path(self, filename):
    class_ref = ClassAssignments.objects.all().get(assignment_id=str(self.id.hex))
    path = os.path.join(MEDIA_ROOT + '/assignment_media/' + class_ref.class_id, str(self.id.hex))
    os.mkdir(path)
    return os.path.join(path, filename)


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    assignment_name = models.CharField(max_length=80, unique=False)
    category_id = models.CharField(max_length=100, unique=False)
    assignment_description = models.CharField(max_length=150, unique=False, null=True)
    points = models.IntegerField()
    created = models.DateTimeField(null=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, auto_now=True)
    assigned = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)
    est_completion_time_min = models.IntegerField(null=True, default=None)
    attached_media = models.FileField(null=True, upload_to=generate_assignment_media_file_path, max_length=300)

    def save(self, *args, **kwargs):
        if self._state.adding:
            try:
                class_ref = ClassAssignments.objects.all().get(assignment_id=str(self.id.hex))
                os.mkdir(os.path.join(MEDIA_ROOT + '/submission_files/' + class_ref.class_id, str(self.id.hex)))
            except:
                pass
        super(Assignment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        class_ref = ClassAssignments.objects.all().get(assignment_id=str(self.id.hex))
        shutil.rmtree(os.path.join(MEDIA_ROOT + '/submission_files/' + class_ref.class_id, str(self.id.hex)))
        shutil.rmtree(os.path.join(MEDIA_ROOT + '/assignment_media/' + class_ref.class_id, str(self.id.hex)))
        super(Assignment, self).save(*args, **kwargs)

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
