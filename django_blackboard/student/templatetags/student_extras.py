from django.template.defaulttags import register


@register.filter
def div_perc(num, denom):
    if num and denom:
        return num * 100.0 / denom


@register.filter
def percent(decimal):
    if decimal:
        return decimal * 100
