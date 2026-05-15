from django import template
from core.models import SystemUser

register = template.Library()

@register.simple_tag
def get_user_role(user):
    if not user.is_authenticated:
        return 'guest'
    
    try:
        system_user = SystemUser.objects.get(user=user)
        return system_user.premission
    except SystemUser.DoesNotExist:
        if user.is_superuser:
            return 'admin'
        return 'dataman'  

@register.filter
def has_role(user, role):
    if not user.is_authenticated:
        return False
    
    try:
        system_user = SystemUser.objects.get(user=user)
        return system_user.premission == role
    except SystemUser.DoesNotExist:
        return user.is_superuser and role == 'admin'