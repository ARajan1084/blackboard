from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.staticfiles import finders


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class EnrollStudentForm(forms.Form):
    klass = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        classes = kwargs.pop('classes')
        students = kwargs.pop('students')
        super(EnrollStudentForm, self).__init__(*args, **kwargs)
        self.fields['klass'].choices = classes
        self.fields['students'] = forms.ModelMultipleChoiceField(queryset=students)


class CreateClassForm(forms.Form):
    course = forms.ChoiceField()
    teacher = forms.ChoiceField()
    period = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        courses = kwargs.pop('courses')
        teachers = kwargs.pop('teachers')
        periods = kwargs.pop('periods')
        super(CreateClassForm, self).__init__(*args, **kwargs)
        self.fields['course'].choices = courses
        self.fields['teacher'].choices = teachers
        self.fields['period'].choices = periods


class CreateCourseForm(forms.Form):
    course_id = forms.CharField(max_length=10)
    course_name = forms.CharField(max_length=32)


class CreateTeacherForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email_address = forms.EmailField()


class CreateStudentForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    student_id = forms.CharField(max_length=7)
    grade = forms.IntegerField()
    email_address = forms.EmailField()


class UploadCSVForm(forms.Form):
    csv = forms.FileField()
