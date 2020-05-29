from django.template.defaulttags import register


@register.filter
def div_perc(num, denom):
    if num and denom:
        return num * 100.0 / denom


@register.filter
def percent(decimal):
    if decimal:
        return decimal * 100


@register.filter
def firm_url(relative, request):
    return request.build_absolute_uri(relative)


@register.filter
def uuid_to_str(uuid):
    return str(uuid).replace('-', '')


@register.filter
def get_thread_field(form, discussion_id):
    return form[discussion_id + '_message'], form[discussion_id + '_media']
