from django import template
from core.models import *

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


@register.simple_tag
def get_employee_attendance_status(employee, date):
    try:
        attendance = Attendance.objects.get(employee=employee, date=date)
        return attendance.get_status_display()
    except Attendance.DoesNotExist:
        return '--'

@register.simple_tag
def get_employee_today_attendance(employee):
    today = date.today()
    try:
        attendance = Attendance.objects.get(employee=employee, date=today)
        return attendance
    except Attendance.DoesNotExist:
        return None

@register.filter
def payment_type_arabic(value):
    types = {
        'monthly': 'شهري',
        'weekly': 'أسبوعي',
        'daily': 'يومي',
        'hourly': 'بالساعة'
    }
    return types.get(value, value)    