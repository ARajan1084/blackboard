from django.template.defaulttags import register


@register.filter
def uuid_to_str(uuid):
    return str(uuid).replace('-', '')
