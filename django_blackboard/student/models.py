import datetime
import pickle
from django.db import models
from django.contrib.auth.models import User
from board.models import Schedule, Class, Course
from django.utils import timezone
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
    cal_credentials = models.FileField(upload_to='tokens/', null=True)

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            student_id = kwargs.pop('student_id')
            auth_calendar = kwargs.pop('auth_calendar')
            super(Student, self).save(*args, **kwargs)
            if auth_calendar is True:
                self.auth_google_calendar(self, student_id=student_id)
        super(Student, self).save(*args, **kwargs)

    def auth_google_calendar(self, student_id):
        scopes = ['https://www.googleapis.com/auth/calendar']
        flow = InstalledAppFlow.from_client_secrets_file(
            '/Users/achintya/blackboard/django_blackboard/student/client_secret.json',
            scopes=scopes)
        credentials = pickle.dumps(flow.run_console())
        self.cal_credentials.save(student_id + '_' + 'token.pkl', ContentFile(credentials))

    def get_calendars(self):
        credentials = pickle.load(open(self.cal_credentials.path, 'rb'))
        service = build('calendar', 'v3', credentials=credentials)
        result = service.calendarList().list().execute()
        return result

    def add_reminder(self, summary, start_date_time, useDefault, override):
        if self.cal_credentials:
            credentials = pickle.load(open(self.cal_credentials.path, 'rb'))
            service = build('calendar', 'v3', credentials=credentials)
            end_date_time = start_date_time + datetime.timedelta(minutes=15)
            id = str(uuid.uuid4().hex)
            event = {
                'summary': summary,
                'location': '',
                'description': '',
                'start': {
                    'dateTime': date_time_str(start_date_time),
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': date_time_str(end_date_time),
                    'timeZone': 'America/Los_Angeles',
                },
                'attendees': [
                ],
                'colorId': {
                    "kind": "calendar#colors",
                    "updated": date_time_str(timezone.now()),
                    "event": {
                        'color': {
                            "background": '1',
                            "foreground": '1'
                        }
                    }
                },
                'reminders': {
                    'useDefault': useDefault,
                    'overrides': [
                        override
                    ],
                },
                'id': id
            }
            service.events().insert(calendarId='primary', body=event).execute()
            return id

    def __str__(self):
        return self.first_name+'_'+self.last_name+'_'+self.student_id

    class Meta:
        db_table = 'students'
        order_with_respect_to = 'student_id'


def next_weekday(date, weekday):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


def date_time_str(date_time):
    return str(date_time.date()) + 'T' + str(date_time.time())


class ClassEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    student_id = models.CharField(max_length=7, unique=False)
    class_id = models.CharField(max_length=100, unique=False)

    def save(self, *args, **kwargs):
        init_events = kwargs.pop('init_events')
        if init_events:
            self.init_events()
        super(ClassEnrollment, self).save(*args, **kwargs)

    def init_events(self):
        student = Student.objects.all().get(student_id=self.student_id)
        credentials = pickle.load(open(student.cal_credentials.path, 'rb'))
        service = build('calendar', 'v3', credentials=credentials)
        klass = Class.objects.all().get(id=uuid.UUID(self.class_id).hex)
        course = Course.objects.all().get(course_id=klass.course_id)
        schedules = Schedule.objects.all().filter(period=klass.period)
        for schedule in schedules:
            date = next_weekday(date=timezone.now(), weekday=schedule.day)
            start_date_time = datetime.datetime.combine(date, schedule.start_time)
            end_date_time = datetime.datetime.combine(date, schedule.end_time)
            event = {
                'summary': course.course_name,
                'location': '',
                'description': '',
                'start': {
                    'dateTime': date_time_str(start_date_time),
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': date_time_str(end_date_time),
                    'timeZone': 'America/Los_Angeles',
                },
                'recurrence': [
                    'RRULE:FREQ=WEEKLY;UNTIL=20200701T170000Z'
                ],
                'attendees': [
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10}
                    ],
                },
            }
            service.events().insert(calendarId='primary', body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

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
    score = models.DecimalField(unique=False, null=True, default=None, decimal_places=2, max_digits=8)
    file = models.FileField(null=True, default=None, unique=False)
    comments = models.CharField(max_length=200, null=True, default=None, unique=False)
    cal_event_id = models.CharField(max_length=50, null=True, default=None, unique=False)
    complete = models.BooleanField(null=True, default=False)

    def __str__(self):
        return self.enrollment_id + '_' + self.assignment_id

    def delete(self, *args, **kwargs):
        enrollment = ClassEnrollment.objects.all().get(id=uuid.UUID(self.enrollment_id))
        student = Student.objects.all().get(student_id=enrollment.student_id)
        try:
            credentials = pickle.load(open(student.cal_credentials.path, 'rb'))
            service = build('calendar', 'v3', credentials=credentials)
            service.events().delete(calendarId='primary', eventId=self.cal_event_id).execute()
        except:
            pass
        finally:
            super(Submission, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'submissions'
        order_with_respect_to = 'assignment_id'


class GradeHistory(models.Model):
    enrollment_id = models.CharField(max_length=36, unique=False)
    date_updated = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.enrollment_id + '_' + str(self.date_updated)

    class Meta:
        db_table = 'grade_history'
        order_with_respect_to = 'enrollment_id'
