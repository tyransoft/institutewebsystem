from decimal import Decimal
import random
from django.db import models
from django.contrib.auth.models import User
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime
# Create your models here.


class SystemUser(models.Model):
    
    PERM={
      ('admin','مدير'),
      ('dataman','مدخل بيانات'),
      ('accountant','محاسب'),

    }
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    premission=models.CharField(max_length=14,choices=PERM)

    def __str__(self):
        return f'{self.user.username}-{self.premission}'
    
    def get_role_display_ar(self):
      return dict(self.PERM).get(self.premission, self.premission)
    
    @classmethod
    def get_admin_count(cls):
        return cls.objects.filter(premission='admin').count()
    
    @classmethod
    def is_last_admin(cls, user):
        if hasattr(user, 'systemuser'):
            if user.systemuser.premission == 'admin':
                return cls.get_admin_count() <= 1
        return False
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.premission == 'admin':
            self.user.is_superuser = True
            self.user.is_staff = True
        else:
            self.user.is_superuser = False
            self.user.is_staff = False
        self.user.save()

class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name='اسم القسم')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'قسم'
        verbose_name_plural = 'الأقسام'

    def __str__(self):
        return self.name

    @property
    def student_count(self):
        return self.students.count()

    @property
    def specialization_count(self):
        return self.specializations.count()


class Specialization(models.Model):
    name = models.CharField(max_length=200, verbose_name='اسم التخصص')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='specializations', verbose_name='القسم')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تخصص'
        verbose_name_plural = 'التخصصات'

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class AcademicSemester(models.Model):
    """نموذج الفصل الدراسي"""
    SEMESTER_TYPES = [
        ('first', 'خريف'),
        ('second', 'ربيع'),
        ('summer', 'صيف'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='اسم الفصل')
    semester_type = models.CharField(max_length=20, choices=SEMESTER_TYPES, verbose_name='نوع الفصل')
    academic_year = models.CharField(max_length=20, verbose_name='العام الدراسي')
    start_date = models.DateField(verbose_name='تاريخ البدء')
    end_date = models.DateField(verbose_name='تاريخ الانتهاء')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'فصل دراسي'
        verbose_name_plural = 'الفصول الدراسية'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} - {self.academic_year}"
    
    def get_semester_type_display_ar(self):
        return dict(self.SEMESTER_TYPES).get(self.semester_type, self.semester_type)    




class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('graduated', 'خريج'),
        ('suspended', 'موقوف'),
    ]
    full_name = models.CharField(max_length=200, verbose_name='الاسم الكامل')
    father_name = models.CharField(max_length=200, verbose_name='اسم الأب')
    phone = models.CharField(max_length=30, blank=True, null=True, verbose_name='الهاتف')
    address = models.TextField(blank=True, null=True, verbose_name='العنوان')
    photo = models.ImageField(upload_to='students/', blank=True, null=True, verbose_name='الصورة')
    registration_number = models.CharField(max_length=50, unique=True, verbose_name='رقم التسجيل')
    nation_number = models.CharField(max_length=20,default='--' , blank=True, null=True, verbose_name='رقم الوطني')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='القسم')
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='التخصص')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')
    total_fees = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='إجمالي الرسوم')
    current_semester = models.ForeignKey(AcademicSemester, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='الفصل الحالي')  
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'طالب'
        verbose_name_plural = 'الطلاب'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.registration_number})"

    def generate_registration_number(self):
        """إنشاء رقم قيد فريد تلقائي"""
        year = datetime.now().strftime('%Y')
        
        last_student = Student.objects.filter(
            registration_number__startswith=f"{year}"
        ).order_by('-registration_number').first()
        
        if last_student and last_student.registration_number:
            try:
                last_number = int(last_student.registration_number.split('-')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        registration_number = f"{year}{new_number:04d}"
        return registration_number

    def generate_registration_number(self):
 

      year = datetime.now().strftime('%y')  

      while True:
        random_digits = random.randint(10000, 99999)

        registration_number = f"{year}{random_digits}"

        if not Student.objects.filter(
            registration_number=registration_number
        ).exists():

            return registration_number
    @property
    def total_paid(self):
        from .models import Payment
        total = Payment.objects.filter(student=self).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return total
 
    def update_total_fees(self):
        from .models import StudentInstallment
        total = StudentInstallment.objects.filter(student=self).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        self.total_fees = total
        self.save(update_fields=['total_fees'])
    
    def save(self, *args, **kwargs):
        
        if not self.registration_number:
            self.registration_number = self.generate_registration_number()
        
        super().save(*args, **kwargs)
        
       
   

    @property
    def balance(self):
        return self.total_fees - self.total_paid

    def get_status_display_ar(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    



class StudentInstallment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'معلق'),
        ('partial', 'جزئي'),
        ('paid', 'مدفوع'),
        ('overdue', 'متأخر'),
    ]
    
    INSTALLMENT_TYPE_CHOICES = [
        ('single', 'قسط واحد'),
        ('monthly', 'تقسيط شهري'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='installments', verbose_name='الطالب')
    semester = models.ForeignKey(AcademicSemester, on_delete=models.CASCADE, related_name='installments', verbose_name='الفصل الدراسي', null=True, blank=True)   
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='إجمالي المبلغ')
    paid_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='المدفوع الكلي')
    due_date = models.DateField(verbose_name='تاريخ الاستحقاق')
    paid_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الدفع الكامل')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        verbose_name = 'قسط طالب'
        verbose_name_plural = 'أقساط الطلاب'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.student.full_name} - {self.amount}"

    @property
    def remaining_amount(self):
        return self.amount - self.paid_amount
    
    @property
    def progress_percentage(self):
        if self.amount > 0:
            return int((self.paid_amount / self.amount) * 100)
        return 0

    def get_status_display_ar(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    





class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'نقداً'),
        ('bank_transfer', 'تحويل مصرفي'),
        ('check', 'شيك'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', verbose_name='الطالب')
    installment = models.ForeignKey(StudentInstallment, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='القسط' , related_name='payments')
    
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='المبلغ')
    payment_date = models.DateField(verbose_name='تاريخ الدفع')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash', verbose_name='طريقة الدفع')
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name='رقم الإيصال')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='سجّل بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'المدفوعات'
        ordering = ['-payment_date']

    def save(self, *args, **kwargs):
        if not self.receipt_number: 
            last_payment = Payment.objects.order_by('-id').first()
            if last_payment and last_payment.receipt_number:
                try:
                    last_num = int(last_payment.receipt_number.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            
            from datetime import date
            date_str = date.today().strftime('%Y%m%d')
            self.receipt_number = f"{date_str}-{new_num:04d}"
        
        super().save(*args, **kwargs)
        
        if self.installment:
            installment = self.installment
            total_paid = installment.payments.aggregate(total=models.Sum('amount'))['total'] or 0
            installment.paid_amount = total_paid
            
            if total_paid >= installment.amount:
                installment.status = 'paid'
                installment.paid_date = self.payment_date
            elif total_paid > 0:
                installment.status = 'partial'
            else:
                installment.status = 'pending'
            
            installment.save()
            
            student = installment.student
            student.update_total_fees()
   
    def __str__(self):
        return f"{self.student.full_name} - {self.amount} - {self.receipt_number}"

    def get_method_display_ar(self):
        return dict(self.METHOD_CHOICES).get(self.payment_method, self.payment_method)
        

   
    def __str__(self):
        return f"{self.student.full_name} - {self.amount} - {self.receipt_number}"

    def get_method_display_ar(self):
        return dict(self.METHOD_CHOICES).get(self.payment_method, self.payment_method)    



class ExpenseCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name='اسم الفئة')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'فئة مصروف'
        verbose_name_plural = 'فئات المصروفات'

    def __str__(self):
        return self.name

    @property
    def total_expenses(self):
        return self.expenses.aggregate(total=models.Sum('amount'))['total'] or 0


class Expense(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان المصروف')
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='المبلغ')
    expense_date = models.DateField(verbose_name='التاريخ')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses', verbose_name='الفئة')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='سجّل بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مصروف'
        verbose_name_plural = 'المصروفات'
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.title} - {self.amount}"


class Employee(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('monthly', 'شهري'),
        ('hourly','بالساعة'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('on_leave', 'في إجازة'),
    ]
    
    full_name = models.CharField(max_length=200, verbose_name='الاسم الكامل')
    position = models.CharField(max_length=200, verbose_name='الوظيفة')
    phone = models.CharField(max_length=30, blank=True, null=True, verbose_name='الهاتف')
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, verbose_name='نظام الدفع')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')
    
    monthly_salary = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='الراتب الشهري')
    expected_work_days = models.IntegerField(default=26, verbose_name='أيام العمل المتوقعة شهرياً')
    
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='أجر الساعة')
    expected_weekly_hours = models.DecimalField(max_digits=10, decimal_places=2, default=40, verbose_name='الساعات المتوقعة أسبوعياً')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفون'
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} - {self.position}"
    
    def get_payment_type_display_ar(self):
        return dict(self.PAYMENT_TYPE_CHOICES).get(self.payment_type, self.payment_type)
    
    @property
    def total_absence_deductions(self):
        return AbsenceRecord.objects.filter(employee=self).aggregate(total=models.Sum('deduction_amount'))['total'] or 0
    
    @property
    def total_monthly_paid(self):
        return MonthlySalaryPayment.objects.filter(employee=self).aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def net_monthly_salary(self):
        return self.monthly_salary - self.total_absence_deductions
    
    @property
    def monthly_remaining(self):
        return self.net_monthly_salary - self.total_monthly_paid
    
    @property
    def total_hours_worked(self):
        return HourlyWorkRecord.objects.filter(employee=self).aggregate(total=models.Sum('hours'))['total'] or 0
    
    @property
    def total_hourly_earned(self):
        return HourlyWorkRecord.objects.filter(employee=self).aggregate(total=models.Sum('total_amount'))['total'] or 0
    
    @property
    def total_hourly_paid(self):
        return HourlyPayment.objects.filter(employee=self).aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def hourly_remaining(self):
        return self.total_hourly_earned - self.total_hourly_paid


class AbsenceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='absences', verbose_name='الموظف')
    absence_date = models.DateField(verbose_name='تاريخ الغياب')
    deduction_amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='قيمة الخصم')
    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name='سبب الغياب')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'تسجيل غياب'
        verbose_name_plural = 'سجل الغيابات'
        ordering = ['-absence_date']
        unique_together = ['employee', 'absence_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.absence_date} - خصم {self.deduction_amount}"


class MonthlySalaryPayment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'نقداً'),
        ('bank_transfer', 'تحويل بنكي'),
        ('check', 'شيك'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='monthly_payments', verbose_name='الموظف')
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='المبلغ المدفوع')
    payment_date = models.DateField(verbose_name='تاريخ الدفع')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash', verbose_name='طريقة الدفع')
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name='رقم الإيصال')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تم بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'دفعة راتب شهري'
        verbose_name_plural = 'مدفوعات الرواتب الشهرية'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.amount} - {self.receipt_number}"
    

    def save(self, *args, **kwargs):
        from core.models import ExpenseCategory, Expense
      
        
        if not self.receipt_number:
            last_payment = MonthlySalaryPayment.objects.order_by('-id').first()
            if last_payment and last_payment.receipt_number:
                try:
                    last_num = int(last_payment.receipt_number)
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            date_str = date.today().strftime('%Y%m%d')
            self.receipt_number = f"{date_str}{new_num:04d}"
        
        
        
        category = ExpenseCategory.objects.first()
        
        if category:
            Expense.objects.create(
                title=f'صرف راتب شهري - {self.employee.full_name}',
                amount=self.amount,
                expense_date=self.payment_date,
                category=category,
                description=f'تسديد راتب للموظف {self.employee.full_name} - إيصال رقم {self.receipt_number}',
                created_by=self.created_by
            )
        super().save(*args, **kwargs)    
    def get_method_display_ar(self):
        return dict(self.METHOD_CHOICES).get(self.payment_method, self.payment_method)


class HourlyWorkRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_records', verbose_name='الموظف')
    work_date = models.DateField(verbose_name='تاريخ العمل')
    hours = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='عدد ساعات العمل')
    hourly_rate_at_time = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='أجر الساعة عند التسجيل')
    total_amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='الإجمالي')
    is_paid = models.BooleanField(default=False, verbose_name='تم التسديد؟')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'سجل ساعات عمل'
        verbose_name_plural = 'سجلات ساعات العمل'
        ordering = ['-work_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.work_date} - {self.hours} ساعات"
    
    def save(self, *args, **kwargs):
        self.hourly_rate_at_time = Decimal(self.employee.hourly_rate)
        self.total_amount = self.hours * self.hourly_rate_at_time
        super().save(*args, **kwargs)


class HourlyPayment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'نقداً'),
        ('bank_transfer', 'تحويل بنكي'),
        ('check', 'شيك'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='hourly_payments', verbose_name='الموظف')
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='المبلغ المدفوع')
    payment_date = models.DateField(verbose_name='تاريخ الدفع')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash', verbose_name='طريقة الدفع')
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name='رقم الإيصال')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تم بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'دفعة موظف بالساعة'
        verbose_name_plural = 'مدفوعات الموظفين بالساعة'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.amount} - {self.receipt_number}"
    

    
    def save(self, *args, **kwargs):
        from core.models import ExpenseCategory, Expense
        from decimal import Decimal
        
        if not self.receipt_number:
            last_payment = HourlyPayment.objects.order_by('-id').first()
            if last_payment and last_payment.receipt_number:
                try:
                    last_num = int(last_payment.receipt_number)
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            date_str = date.today().strftime('%Y%m%d')
            self.receipt_number = f"{date_str}{new_num:04d}"
        
        
        unpaid_records = HourlyWorkRecord.objects.filter(employee=self.employee, is_paid=False).order_by('work_date')
        remaining_to_pay = Decimal(str(self.amount))
        for record in unpaid_records:
            if remaining_to_pay <= 0:
                break
            if Decimal(str(record.total_amount)) <= remaining_to_pay:
                record.is_paid = True
                remaining_to_pay -= Decimal(str(record.total_amount))
            else:
                record.is_paid = False
            record.save()
        
        category = ExpenseCategory.objects.first()
        
        if category:
            Expense.objects.create(
                title=f'صرف مستحقات بالساعة - {self.employee.full_name}',
                amount=self.amount,
                expense_date=self.payment_date,
                category=category,
                description=f'تسديد مستحقات للموظف {self.employee.full_name} - إيصال رقم {self.receipt_number}',
                created_by=self.created_by
            )
        super().save(*args, **kwargs)
    def get_method_display_ar(self):
        return dict(self.METHOD_CHOICES).get(self.payment_method, self.payment_method)