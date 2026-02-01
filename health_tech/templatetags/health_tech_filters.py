from django import template

register = template.Library()

@register.filter
def lookup(d, key):
    """Template filter to look up dictionary values by key"""
    return d.get(key, 0) if isinstance(d, dict) else 0