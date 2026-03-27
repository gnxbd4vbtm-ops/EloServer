from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get value from a dictionary safely."""
    return dictionary.get(key)
