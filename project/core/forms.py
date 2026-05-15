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
            'nation_number', 'department', 'specialization', 'status'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs=WIDGET_ATTRS),
            'father_name': forms.TextInput(attrs=WIDGET_ATTRS),
            'phone': forms.TextInput(attrs=WIDGET_ATTRS),
            'address': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 2}),
            'nation_number':forms.TextInput(attrs=WIDGET_ATTRS),
            'department': forms.Select(attrs=SELECT_ATTRS),
            'specialization': forms.Select(attrs=SELECT_ATTRS),
            'status': forms.Select(attrs=SELECT_ATTRS),
        }
        labels = {
            'full_name': 'الاسم الكامل',
            'father_name': 'اسم الأب',
            'phone': 'الهاتف',
            'address': 'العنوان',
            'photo': 'الصورة',
            'nation_number':'الرقم الوطني',
            'department': 'القسم',
            'specialization': 'التخصص',
            'status': 'الحالة',
        }


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




class InstallmentForm(forms.ModelForm):
    class Meta:
        model = StudentInstallment
        fields = ['student', 'amount', 'installment_type', 'number_of_months', 'due_date', 'notes']
        widgets = {
            'student': forms.Select(attrs=SELECT_ATTRS),
            'amount': forms.NumberInput(attrs=WIDGET_ATTRS),
            'installment_type': forms.Select(attrs=SELECT_ATTRS),
            'number_of_months': forms.NumberInput(attrs=WIDGET_ATTRS),
            'due_date': forms.DateInput(attrs=DATE_ATTRS),
            'notes': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 2}),
        }
        labels = {
            'student': 'الطالب',
            'amount': 'إجمالي المبلغ',
            'installment_type': 'نوع التقسيط',
            'number_of_months': 'عدد الأشهر (للأقساط الشهرية)',
            'due_date': 'تاريخ الاستحقاق الأول',
            'notes': 'ملاحظات',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        installment_type = cleaned_data.get('installment_type')
        number_of_months = cleaned_data.get('number_of_months')
        amount = cleaned_data.get('amount')
        
        if installment_type == 'monthly' and number_of_months and number_of_months < 2:
            self.add_error('number_of_months', 'عدد الأشهر يجب أن يكون 2 على الأقل للتقسيط الشهري')
        
        if installment_type == 'monthly' and number_of_months and amount:
            if amount % number_of_months != 0:
                self.add_error('amount', f'المبلغ {amount} غير قابل للقسمة على {number_of_months} أشهر. يرجى تعديل المبلغ أو عدد الأشهر')
        
        return cleaned_data




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

class MonthlyPaymentForm(forms.Form):
    """نموذج تسديد قسط شهري محدد"""
    amount = forms.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        label='المبلغ المدفوع',
        widget=forms.NumberInput(attrs={
            **WIDGET_ATTRS, 
            'min': 1,
            'step': 1,
            'placeholder': 'أدخل المبلغ المراد دفعه'
        })
    )
    payment_date = forms.DateField(
        label='تاريخ الدفع',
        widget=forms.DateInput(attrs=DATE_ATTRS)
    )
    payment_method = forms.ChoiceField(
        choices=Payment.METHOD_CHOICES,
        label='طريقة الدفع',
        widget=forms.Select(attrs=SELECT_ATTRS)
    )
    notes = forms.CharField(
        required=False,
        label='ملاحظات',
        widget=forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 2})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import date
        if not self.data.get('payment_date'):
            self.initial['payment_date'] = date.today()
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('يجب أن يكون المبلغ أكبر من صفر')
        return amount                                 