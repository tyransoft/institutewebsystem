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
        return f"{self.get_semester_type_display()} - {self.academic_year}"
    
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


