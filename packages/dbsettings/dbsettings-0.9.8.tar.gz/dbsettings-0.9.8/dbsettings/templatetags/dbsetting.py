from django import template
from dbsettings.functions import getValue

register = template.Library()

@register.simple_tag
def dbsetting(key, default=""):
    return getValue(key, default)
