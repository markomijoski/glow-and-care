from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Safely update or add URL parameters without losing existing ones.
    Usage: {% url_replace page=2 category='serums' %}
    """
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        if value is None or value == '':
            if key in query:
                del query[key]
        else:
            query[key] = value
    return query.urlencode()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0
