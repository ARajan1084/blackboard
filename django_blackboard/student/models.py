import pickle
from django.db import models
from django.contrib.auth.models import User
from board.models import Schedule, Class
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.core.files.base import ContentFile
import uuid


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    student_id = models.CharField(max_length=7, primary_key=True)
    grade = models.IntegerField(unique=False, default=11)
    id_picture = models.ImageField(upload_to='media/id_pictures')
    email_address = models.CharField(max_length=320, null=True)
    cal_credentials = models.FileField(upload_to='tokens/5171991', null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            scopes = ['https://www.googleapis.com/auth/calendar']
            flow = InstalledAppFlow.from_client_secrets_file("/Users/achintya/Downloads/client_secret.json",
                                                             scopes=scopes)
            credentials = pickle.dumps(flow.run_console())
            file = ContentFile(credentials)
            self.cal_credentials.save('token.pkl', file)
        super(Student, self).save(*args, **kwargs)

    def get_events(self):
        credentials = pickle.load(open(self.cal_credentials.path, 'rb'))
        service = build('calendar', 'v3', credentials=credentials)
        result = service.calendarList().list().execute()
        return result

    def __str__(self):
        return self.first_name+'_'+self.last_name+'_'+self.student_id

    class Meta:
        db_table = 'students'
        order_with_respect_to = 'student_id'


class ClassEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    student_id = models.CharField(max_length=7, unique=False)
    class_id = models.CharField(max_length=100, unique=False)

    def save(self, *args, **kwargs):
        student = Student.objects.all().get(student_id=self.student_id)
        klass = Class.objects.all().get(id=uuid.UUID(self.class_id).hex)
        schedule = Schedule.objects.all().filter(period=klass.period)
        super(ClassEnrollment, self).save(*args, **kwargs)

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
