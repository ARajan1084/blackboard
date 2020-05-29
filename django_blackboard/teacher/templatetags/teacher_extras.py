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


@register.filter
def name(person):
    return person.first_name + ' ' + person.last_name


@register.filter
def get_item(dict, key):
    return dict.get(key)


@register.filter
def get_element(list, index):
    if list:
        return list[index]


@register.filter
def get_thread_field(form, discussion_id):
    return form[discussion_id + '_message'], form[discussion_id + '_media']
