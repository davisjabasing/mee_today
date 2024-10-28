from django import template

register = template.Library()

@register.filter
def other_user(appointment, user):
    if appointment.requester == user:
        return appointment.recipient.username
    return appointment.requester.username
