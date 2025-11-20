from django import template
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={'class': css})

@register.filter(name='has_staff_role')
def has_staff_role(user):
    try:
        return (user.is_authenticated and (user.profile.role == 'STAFF' or user.is_staff))
    except Exception:
        return user.is_staff if hasattr(user, 'is_staff') else False
