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
