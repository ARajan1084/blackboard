from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime


class Score(forms.Form):
    score = forms.IntegerField(required=False)


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class CreateAssignmentForm(forms.Form):
    category = forms.ChoiceField()
    name = forms.CharField()
    description = forms.CharField(required=False)
    points = forms.IntegerField()
    due_date = forms.DateTimeField(widget=DateInput, required=False)
    due_time = forms.TimeField(widget=TimeInput, required=False)

    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        super(CreateAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = self.categories
