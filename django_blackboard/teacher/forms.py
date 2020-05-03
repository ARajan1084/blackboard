from django import forms


class Scores(forms.Form):
    def __init__(self, *args, **kwargs):
        student_scores = kwargs.pop('student_scores')
        super(Scores, self).__init__(*args, **kwargs)
        for student_score in student_scores:
            self.fields[student_score[0].student_id] = forms.IntegerField(required=False, initial=student_score[1])


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class CreateCategoryForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(required=False)
    weight = forms.DecimalField(required=False)


class EditCategoriesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories')
        super(EditCategoriesForm, self).__init__(*args, **kwargs)
        for category in categories:
            self.fields[str(category.id.hex)] = forms.DecimalField(required=False, initial=category.category_weight)


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
