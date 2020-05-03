from django.template.defaulttags import register


@register.filter
def get_field(form, student):
    return form[student.student_id]


@register.filter
def uuid_to_str(uuid):
    return str(uuid).replace('-', '')


@register.filter
def assign_student(input, student):
    input.add_student(student)


@register.filter
def percentage(value):
    return format(value, '%')


@register.filter
def get_edit_field(form, category):
    return form[str(category.id.hex)]