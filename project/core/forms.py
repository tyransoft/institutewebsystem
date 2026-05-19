from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

WIDGET_ATTRS = {
    'class': 'form-control',
    'placeholder': 'أدخل النص هنا'
}

SELECT_ATTRS = {
    'class': 'form-select'
}

DATE_ATTRS = {
    'class': 'form-control',
    'type': 'date'
      
}


class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        label='الاسم', 
        required=True,
        widget=forms.TextInput(attrs=WIDGET_ATTRS)
    )
    premission = forms.ChoiceField(
        choices=SystemUser.PERM, 
        label='الصلاحية', 
        widget=forms.Select(attrs=SELECT_ATTRS)
    )
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs=WIDGET_ATTRS),
        }
        labels = {
            'username': 'اسم المستخدم',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(WIDGET_ATTRS)
        self.fields['password2'].widget.attrs.update(WIDGET_ATTRS)
        self.fields['password1'].label = 'كلمة المرور'
        self.fields['password2'].label = 'تأكيد كلمة المرور'
        
        self.order_fields(['username', 'first_name', 'premission', 'password1', 'password2'])
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('اسم المستخدم موجود مسبقاً')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)        
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = ''
        premission = self.cleaned_data.get('premission')
        user.is_superuser = (premission == 'admin')
        user.is_staff = (premission == 'admin')          
        if commit:
            user.save()
            SystemUser.objects.create(
                user=user,
                premission=premission
            )
        return user


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        label='الاسم', 
        required=True,
        widget=forms.TextInput(attrs=WIDGET_ATTRS)
    )
    premission = forms.ChoiceField(
        choices=SystemUser.PERM, 
        label='الصلاحية', 
        widget=forms.Select(attrs=SELECT_ATTRS)
    )
    
    class Meta:
        model = User
        fields = []  
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.first_name
            
            try:
                system_user = SystemUser.objects.get(user=self.instance)
                self.fields['premission'].initial = system_user.premission
            except SystemUser.DoesNotExist:
                self.fields['premission'].initial = 'dataman'
    
    def clean(self):
        cleaned_data = super().clean()
        premission = cleaned_data.get('premission')
        old_premission = None
        
        try:
            system_user = SystemUser.objects.get(user=self.instance)
            old_premission = system_user.premission
        except SystemUser.DoesNotExist:
            pass
        
        if old_premission == 'admin' and premission != 'admin':
            admin_count = SystemUser.objects.filter(premission='admin').exclude(user=self.instance).count()
            if admin_count == 0:
                raise forms.ValidationError('لا يمكن تغيير صلاحية المدير الوحيد في النظام. يجب أن يكون هناك مدير واحد على الأقل')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)       
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = ''
        premission = self.cleaned_data.get('premission')
        user.is_superuser = (premission == 'admin')
        user.is_staff = (premission == 'admin')
        
        if commit:
            user.save()
            SystemUser.objects.update_or_create(
                user=user,
                defaults={'premission': premission}
            )
        return user







class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'full_name', 'father_name', 'phone', 'address', 'photo',
            'nation_number', 'department', 'specialization', 'status', 'current_semester'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs=WIDGET_ATTRS),
            'father_name': forms.TextInput(attrs=WIDGET_ATTRS),
            'phone': forms.TextInput(attrs=WIDGET_ATTRS),
            'address': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 2}),
            'nation_number': forms.TextInput(attrs={**WIDGET_ATTRS, 'required': False}),
            'department': forms.Select(attrs=SELECT_ATTRS),
            'specialization': forms.Select(attrs=SELECT_ATTRS),
            'status': forms.Select(attrs=SELECT_ATTRS),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'current_semester': forms.Select(attrs=SELECT_ATTRS),
        }
        labels = {
            'full_name': 'الاسم الكامل',
            'father_name': 'اسم الأب',
            'phone': 'الهاتف',
            'address': 'العنوان',
            'photo': 'الصورة الشخصية',
            'nation_number': 'الرقم الوطني (اختياري)',
            'department': 'القسم',
            'specialization': 'التخصص',
            'status': 'الحالة',
            'current_semester': 'الفصل الدراسي الحالي',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nation_number'].required = False
        self.fields['current_semester'].required = False
        self.order_fields([
            'full_name', 'father_name', 'phone', 'address', 'photo',
            'nation_number', 'department', 'specialization', 'status', 'current_semester'
        ])
    
    def clean_nation_number(self):
        """التحقق من uniqueness مع السماح بقيم فارغة"""
        nation_number = self.cleaned_data.get('nation_number')
        if nation_number:
            if Student.objects.filter(nation_number=nation_number).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('هذا الرقم الوطني مسجل مسبقاً')
        return nation_number


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
        }
        labels = {'name': 'اسم القسم', 'description': 'الوصف'}


class SpecializationForm(forms.ModelForm):
    class Meta:
        model = Specialization
        fields = ['name', 'department', 'description']
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'department': forms.Select(attrs=SELECT_ATTRS),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
        }
        labels = {'name': 'اسم التخصص', 'department': 'القسم', 'description': 'الوصف'}







class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'expense_date', 'category', 'description']
        widgets = {
            'title': forms.TextInput(attrs=WIDGET_ATTRS),
            'amount': forms.NumberInput(attrs=WIDGET_ATTRS),
            'expense_date': forms.DateInput(attrs=DATE_ATTRS),
            'category': forms.Select(attrs=SELECT_ATTRS),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
        }
        labels = {
            'title': 'عنوان المصروف',
            'amount': 'المبلغ (دينار)',
            'expense_date': 'التاريخ',
            'category': 'الفئة',
            'description': 'الوصف',
        }


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'description': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
        }
        labels = {'name': 'اسم الفئة', 'description': 'الوصف'}            
                                
class InstallmentForm(forms.ModelForm):
    class Meta:
        model = StudentInstallment
        fields = ['student', 'semester', 'amount', 'due_date', 'notes']
        widgets = {
            'student': forms.Select(attrs=SELECT_ATTRS),
            'semester': forms.Select(attrs=SELECT_ATTRS),
            'amount': forms.NumberInput(attrs=WIDGET_ATTRS),
            'due_date': forms.DateInput(attrs=DATE_ATTRS),
            'notes': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 2}),
        }
        labels = {
            'student': 'الطالب',
            'semester': 'الفصل الدراسي',
            'amount': 'المبلغ',
            'due_date': 'تاريخ الاستحقاق',
            'notes': 'ملاحظات',
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'installment', 'amount', 'payment_date', 'payment_method', 'notes']
        widgets = {
            'student': forms.Select(attrs=SELECT_ATTRS),
            'installment': forms.Select(attrs=SELECT_ATTRS),
            'amount': forms.NumberInput(attrs=WIDGET_ATTRS),
            'payment_date': forms.DateInput(attrs=DATE_ATTRS),
            'payment_method': forms.Select(attrs=SELECT_ATTRS),
            'notes': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 2}),
        }
        labels = {
            'student': 'الطالب',
            'installment': 'القسط',
            'amount': 'المبلغ',
            'payment_date': 'تاريخ الدفع',
            'payment_method': 'طريقة الدفع',
            'notes': 'ملاحظات',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import date
        if not self.data.get('payment_date'):
            self.initial['payment_date'] = date.today()
        
        self.fields['installment'].queryset = StudentInstallment.objects.exclude(status='paid')


class SemesterForm(forms.ModelForm):
    class Meta:
        model = AcademicSemester
        fields = ['name', 'semester_type', 'academic_year', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_ATTRS),
            'semester_type': forms.Select(attrs=SELECT_ATTRS),
            'academic_year': forms.TextInput(attrs=WIDGET_ATTRS),
            'start_date': forms.DateInput(attrs=DATE_ATTRS),
            'end_date': forms.DateInput(attrs=DATE_ATTRS),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'اسم الفصل',
            'semester_type': 'نوع الفصل',
            'academic_year': 'العام الدراسي',
            'start_date': 'تاريخ البدء',
            'end_date': 'تاريخ الانتهاء',
            'is_active': 'فصل نشط',
        }                               