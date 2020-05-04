from django import forms


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


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
