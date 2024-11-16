from django import template

register = template.Library()

@register.filter
def other_user(appointment, user):
    if appointment.requester == user:
        return appointment.recipient.username
    return appointment.requester.username




@register.filter(name='get_attribute')
def get_attribute(obj, attr, default=None):
    return getattr(obj, attr, default)