"""
Custom template tags for Jazzmin compatibility with Django 5.2+
Restores the length_is filter that was removed in Django 5.0
"""
from django import template

register = template.Library()


@register.filter(name='length_is')
def length_is(value, arg):
    """
    Returns True if the length of the value is equal to the argument.
    This filter was removed in Django 5.0 but is still used by Jazzmin templates.
    
    Usage: {% if value|length_is:3 %}
    """
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return False
