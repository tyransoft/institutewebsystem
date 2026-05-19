from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(SystemUser)
admin.site.register(Student)
admin.site.register(StudentInstallment)
admin.site.register(AcademicSemester)
admin.site.register(Payment)