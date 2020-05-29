from django import forms


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ThreadReplyForm(forms.Form):
    def add_field(self, discussion_id):
        self.fields[discussion_id + '_message'] = forms.CharField(max_length=200)
        self.fields[discussion_id + '_media'] = forms.FileField(required=False)
        return self.fields[discussion_id + '_message'], self.fields[discussion_id + '_media']