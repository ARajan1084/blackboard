from django import forms


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ThreadReplyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        discussions = kwargs.pop('discussions')
        super(ThreadReplyForm, self).__init__(*args, **kwargs)
        for discussion in discussions:
            self.add_field(discussion_id=str(discussion.id.hex))

    def add_field(self, discussion_id):
        self.fields[discussion_id + '_message'] = forms.CharField(max_length=200, required=False)
        self.fields[discussion_id + '_media'] = forms.FileField(required=False)
        return self.fields[discussion_id + '_message'], self.fields[discussion_id + '_media']


class NewThreadForm(forms.Form):
    title = forms.CharField(required=True)
    message = forms.CharField(max_length=200, required=True)
    media = forms.FileField(required=False)