from django.template.defaulttags import register


@register.filter
def percent(decimal):
    return decimal * 100