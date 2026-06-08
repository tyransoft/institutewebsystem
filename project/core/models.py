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
        ('weekly', 'أسبوعي'),
        ('daily', 'يومي (نهاية اليوم)'),
        ('hourly', 'بالمساحة (نهاية اليوم)'),
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
    
    monthly_salary = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='الراتب الشهري (للموظف الشهري)')
    expected_work_days = models.IntegerField(default=26, verbose_name='أيام العمل المتوقعة شهرياً')
    
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='أجر الساعة (للموظف بالساعة)')
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


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('absent', 'غائب'),
        ('late', 'متأخر'),
        ('excused', 'بعذر'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances', verbose_name='الموظف')
    date = models.DateField(verbose_name='التاريخ')
    
    check_in_time = models.TimeField(blank=True, null=True, verbose_name='وقت الحضور')
    check_out_time = models.TimeField(blank=True, null=True, verbose_name='وقت الانصراف')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present', verbose_name='الحالة')
    hours_worked = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='عدد ساعات العمل')
    
    deduction_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='مبلغ الخصم')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'حضور'
        verbose_name_plural = 'الحضور والغياب'
        ordering = ['-date']
        unique_together = ['employee', 'date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_status_display()}"
    
    def calculate_hours_worked(self):
        if self.check_in_time and self.check_out_time:
            from datetime import datetime as dt
            check_in = dt.combine(self.date, self.check_in_time)
            check_out = dt.combine(self.date, self.check_out_time)
            diff = check_out - check_in
            hours = diff.total_seconds() / 3600
            return round(hours, 2)
        return 0
    
    def calculate_deduction(self):
        deduction = 0
        if self.status == 'absent':
            if self.employee.payment_type == 'monthly':
                daily_rate = self.employee.monthly_salary / self.employee.expected_work_days
                deduction = daily_rate
            elif self.employee.payment_type == 'daily':
                deduction = self.employee.hourly_rate * 8
            elif self.employee.payment_type == 'hourly':
                deduction = self.employee.hourly_rate * self.employee.expected_weekly_hours / 5
        elif self.status == 'late' and self.employee.payment_type == 'hourly':
            if self.check_in_time:
                expected_hour = 9
                if self.check_in_time.hour > expected_hour:
                    late_hours = self.check_in_time.hour - expected_hour
                    deduction = late_hours * self.employee.hourly_rate
        return round(deduction)
    
    def save(self, *args, **kwargs):
        if self.check_in_time and self.check_out_time:
            self.hours_worked = self.calculate_hours_worked()
        self.deduction_amount = self.calculate_deduction()
        super().save(*args, **kwargs)


class Payroll(models.Model):
    STATUS_CHOICES = [
        ('pending', 'معلق'),
        ('paid', 'مدفوع'),
        ('cancelled', 'ملغي'),
    ]
    
    PAYROLL_TYPE_CHOICES = [
        ('monthly', 'شهري'),
        ('weekly', 'أسبوعي'),
        ('daily', 'يومي'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls', verbose_name='الموظف')
    payroll_type = models.CharField(max_length=20, choices=PAYROLL_TYPE_CHOICES, verbose_name='نوع المرتب')
    
    period_start = models.DateField(verbose_name='بداية الفترة')
    period_end = models.DateField(verbose_name='نهاية الفترة')
    
    base_salary = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='المرتب الأساسي')
    total_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='إجمالي الساعات')
    total_deductions = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='إجمالي الخصومات')
    
    net_salary = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='صافي المرتب')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    payment_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الدفع')
    
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تم بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'كشف راتب'
        verbose_name_plural = 'كشوف الرواتب'
        ordering = ['-period_end']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.period_start} إلى {self.period_end}"
    
    def calculate_payroll(self):
        absences = Attendance.objects.filter(
            employee=self.employee,
            date__range=[self.period_start, self.period_end],
            status='absent'
        ).count()
        
        late_days = Attendance.objects.filter(
            employee=self.employee,
            date__range=[self.period_start, self.period_end],
            status='late'
        ).count()
        
        total_deduction = 0
        
        if self.employee.payment_type == 'monthly':
            daily_rate = self.employee.monthly_salary / self.employee.expected_work_days
            total_deduction = absences * daily_rate
            self.base_salary = self.employee.monthly_salary
        
        elif self.employee.payment_type == 'weekly':
            attendances = Attendance.objects.filter(
                employee=self.employee,
                date__range=[self.period_start, self.period_end],
                status='present'
            )
            total_hours = sum([a.hours_worked for a in attendances])
            self.total_hours = total_hours
            self.base_salary = total_hours * self.employee.hourly_rate
            total_deduction = attendances.filter(status='absent').count() * (self.employee.hourly_rate * 8)
        
        elif self.employee.payment_type in ['daily', 'hourly']:
            attendances = Attendance.objects.filter(
                employee=self.employee,
                date__range=[self.period_start, self.period_end]
            )
            self.total_hours = sum([a.hours_worked for a in attendances if a.status == 'present'])
            self.base_salary = self.total_hours * self.employee.hourly_rate
            total_deduction = sum([a.deduction_amount for a in attendances])
        
        self.total_deductions = round(total_deduction)
        self.net_salary = round(self.base_salary - self.total_deductions)
        return self.net_salary
    
    def save(self, *args, **kwargs):
        self.calculate_payroll()
        super().save(*args, **kwargs)


class PayrollPayment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'نقداً'),
        ('bank_transfer', 'تحويل بنكي'),
        ('check', 'شيك'),
    ]
    
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='payments', verbose_name='كشف الراتب')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='الموظف')
    
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='المبلغ المدفوع')
    payment_date = models.DateField(verbose_name='تاريخ الدفع')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash', verbose_name='طريقة الدفع')
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name='رقم الإيصال')
    
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تم بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'تسديد راتب'
        verbose_name_plural = 'تسديد الرواتب'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.amount} - {self.receipt_number}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            last_payment = PayrollPayment.objects.order_by('-id').first()
            if last_payment and last_payment.receipt_number:
                try:
                    last_num = int(last_payment.receipt_number.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            date_str = date.today().strftime('%Y%m%d')
            self.receipt_number = f"SLR-{date_str}-{new_num:04d}"
        
        super().save(*args, **kwargs)
        self.payroll.status = 'paid'
        self.payroll.payment_date = self.payment_date
        self.payroll.save(update_fields=['status', 'payment_date'])
    
    def get_method_display_ar(self):
        return dict(self.METHOD_CHOICES).get(self.payment_method, self.payment_method)