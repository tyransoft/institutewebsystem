from django.http import JsonResponse,HttpResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import *
from django.db.models import  Q,Sum ,Count 
from django.core.paginator import Paginator
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from reportlab.lib.colors import HexColor, white
from bidi.algorithm import get_display
import arabic_reshaper
from datetime import date, timedelta
from django.utils import timezone
from django.db import transaction


def user_login(request):
   if request.method =='POST':
      username=request.POST.get('username')
      password=request.POST.get('password')
      if username and password:
         user=authenticate(request,username=username,password=password)
         if user is not None:
           login(request,user)
           messages.success(request,'تم تسجيل الدخول بنجاح')
           return redirect('dashboard')
      else:
         messages.error(request,'اسم المستخدم وكلمة المرور بيانات مطلوبة')
         return redirect('user_login')
   return  render(request, 'login.html' )

@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')

@login_required
def user_create(request):
        
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save() 
            messages.success(request, f' تم إضافة المستخدم {user.username} بنجاح')
            return redirect('user_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f' {form.fields.get(field, field).label}: {error}')
    else:
        form = UserCreateForm()
    
    return render(request, 'user_form.html', {
        'form': form,
        'is_update': False,
        'title': 'إضافة مستخدم جديد'
    })


@login_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'تم تحديث بيانات المستخدم {user.username} بنجاح')
                return redirect('user_list')
            except forms.ValidationError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields.get(field, field).label}: {error}')
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'user_form.html', {
        'form': form,
        'is_update': True,
        'title': 'تعديل بيانات المستخدم',
        'user_obj': user
    })

@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    username = user.username
    if request.user.pk == user.pk:
        messages.error(request, 'لا يمكنك حذف حساب المستخدم الخاص بك')
        return redirect('user_list')
    
    is_admin = False
    try:
        system_user = SystemUser.objects.get(user=user)
        is_admin = (system_user.premission == 'admin')
    except SystemUser.DoesNotExist:
        pass
    
    if is_admin:
        admin_count = SystemUser.objects.filter(premission='admin').exclude(user=user).count()
        
        if admin_count == 0:
            messages.error(request, 'لا يمكن حذف المدير الوحيد في النظام. يجب أن يكون هناك مدير واحد على الأقل')
            return redirect('user_list')
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'تم حذف المستخدم {username} بنجاح')
        return redirect('user_list')
    
    return render(request, 'confirm_delete.html', {
        'object': username,
        
    })


@login_required
def user_list(request):
    users=SystemUser.objects.all()
    return render(request, 'user_list.html', {'users': users})




@login_required
def department_list(request):
    departments = Department.objects.all()
    specializations = Specialization.objects.select_related('department').all()
    context = {
        'departments': departments,
        'specializations': specializations,
    }
    return render(request, 'department_list.html', context)


@login_required
def department_add(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة القسم بنجاح')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'department_form.html', {'form': form})


@login_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث القسم')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'department_form.html', {'form': form})


@login_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'تم حذف القسم')
        return redirect('department_list')
    return render(request, 'confirm_delete.html', {'object': department})


@login_required
def specialization_add(request):
    if request.method == 'POST':
        form = SpecializationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة التخصص بنجاح')
            return redirect('department_list')
    else:
        form = SpecializationForm()
    return render(request, 'specialization_form.html', {'form': form})


@login_required
def specialization_edit(request, pk):
    specialization = get_object_or_404(Specialization, pk=pk)
    if request.method == 'POST':
        form = SpecializationForm(request.POST, instance=specialization)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث التخصص')
            return redirect('department_list')
    else:
        form = SpecializationForm(instance=specialization)
    return render(request, 'specialization_form.html', {'form': form})


@login_required
def specialization_delete(request, pk):
    specialization = get_object_or_404(Specialization, pk=pk)
    if request.method == 'POST':
        specialization.delete()
        messages.success(request, 'تم حذف التخصص')
        return redirect('department_list')
    return render(request, 'confirm_delete.html', {'object': specialization})

@login_required
def semester_list(request):
    semesters = AcademicSemester.objects.all().order_by('-start_date')
    return render(request, 'semester_list.html', {'semesters': semesters})


@login_required
def semester_add(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الفصل الدراسي بنجاح')
            return redirect('semester_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج')
    else:
        form = SemesterForm()
    
    return render(request, 'semester_form.html', {'form': form, 'title': 'إضافة فصل دراسي'})


@login_required
def semester_edit(request, pk):
    semester = get_object_or_404(AcademicSemester, pk=pk)
    if request.method == 'POST':
        form = SemesterForm(request.POST, instance=semester)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الفصل الدراسي بنجاح')
            return redirect('semester_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج')
    else:
        form = SemesterForm(instance=semester)
    
    return render(request, 'semester_form.html', {'form': form, 'title': 'تعديل فصل دراسي'})


@login_required
def semester_delete(request, pk):
    semester = get_object_or_404(AcademicSemester, pk=pk)
    if request.method == 'POST':
        semester.delete()
        messages.success(request, 'تم حذف الفصل الدراسي بنجاح')
        return redirect('semester_list')
    
    return render(request, 'confirm_delete.html', {'object': semester})

@login_required
def student_list(request):
    qs = Student.objects.select_related('department', 'specialization').order_by('-created_at')
    q = request.GET.get('q', '')
    dept = request.GET.get('department', '')
    status = request.GET.get('status', '')
    year = request.GET.get('year', '')
    
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(registration_number__icontains=q) |
            Q(phone__icontains=q)
        )
    if dept:
        qs = qs.filter(department_id=dept)
    if status:
        qs = qs.filter(status=status)
    if year:
        qs = qs.filter(academic_year=year)
    
    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    
    context = {
        'students': students,
        'departments': Department.objects.all(),
        'q': q,
        'selected_dept': dept,
        'selected_status': status,
        'selected_year': year,
        'status_choices': Student.STATUS_CHOICES,
    }
    return render(request, 'student_list.html', context)


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related('department', 'specialization'), pk=pk)
    context = {
        'student': student,
        'installments':'moad',
        'total_paid': student.total_paid,
        'balance': student.balance,
        'total_fees': student.total_fees,
    }
    return render(request, 'student_detail.html', context)


@login_required
def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الطالب بنجاح')
            return redirect('student_list')
    else:
        form = StudentForm()
    semesters=AcademicSemester.objects.all()    
    return render(request, 'student_form.html', {'form': form,'semesters':semesters})


@login_required
def installment_edit(request, pk):
    installment = get_object_or_404(StudentInstallment, pk=pk)
    old_student = installment.student
    
    if request.method == 'POST':
        form = InstallmentForm(request.POST, instance=installment)
        if form.is_valid():
            with transaction.atomic():
                installment = form.save(commit=False)
                
                if installment.paid_amount > installment.amount:
                    messages.error(request, 'المبلغ المدفوع لا يمكن أن يتجاوز إجمالي القسط')
                    return render(request, 'installment_form.html', {
                        'form': form, 
                        'title': 'تعديل القسط',
                        'installment': installment
                    })
                
                if installment.paid_amount >= installment.amount:
                    installment.status = 'paid'
                elif installment.paid_amount > 0:
                    installment.status = 'partial'
                else:
                    installment.status = 'pending'
                
                installment.save()
                
                if old_student != installment.student:
                    old_student.update_total_fees()
                    installment.student.update_total_fees()
                else:
                    installment.student.update_total_fees()
                
                messages.success(request, f'تم تعديل القسط #{installment.id} بنجاح')
                return redirect('finance')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج')
    else:
        form = InstallmentForm(instance=installment)
    
    return render(request, 'installment_form.html', {
        'form': form, 
        'title': 'تعديل القسط',
        'installment': installment
    })


@login_required
def installment_delete(request, pk):
    installment = get_object_or_404(StudentInstallment, pk=pk)
    student = installment.student
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                installment_id = installment.id
                installment.delete()
                
                student.update_total_fees()
                
                messages.success(request, f'تم حذف القسط #{installment_id} بنجاح')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'تم الحذف بنجاح'})
                
                return redirect('finance')
                
        except Exception as e:
            error_message = f'حدث خطأ أثناء حذف القسط: {str(e)}'
            messages.error(request, error_message)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})
    
    return render(request, 'installment_confirm_delete.html', {
        'installment': installment,
        'student': student
    })


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST,request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات الطالب')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'student_form.html', {'form': form})


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'تم حذف الطالب')
        return redirect('student_list')
    return render(request, 'confirm_delete.html', {'object': student})


@login_required
def search_students(request):
    query = request.GET.get('q', '')
    if query:
        students = Student.objects.filter(
            Q(full_name__icontains=query) |
            Q(registration_number__icontains=query)
        )[:20]
    else:
        students = Student.objects.all()[:20]
    
    results = [{
        'id': s.id,
        'text': f"{s.full_name} ({s.registration_number})",
    } for s in students]
    
    return JsonResponse({'results': results})
@login_required
def search_installments(request):
    student_id = request.GET.get('student_id', '')
    query = request.GET.get('q', '')
    
    installments = StudentInstallment.objects.filter(
        status__in=['pending', 'partial', 'overdue']
    ).select_related('student')
    
    if student_id:
        installments = installments.filter(student_id=student_id)
    
    if query:
        installments = installments.filter(
            Q(student__full_name__icontains=query) |
            Q(student__registration_number__icontains=query)
        )
    
    installments = installments[:20]
    
    results = [{
        'id': i.id,
        'text': f"قسط {i.amount} د.ل - استحقاق {i.due_date} - {i.student.full_name}",
        'amount': str(i.amount),
        'remaining': str(i.remaining_amount),
        'due_date': str(i.due_date)
    } for i in installments]
    
    return JsonResponse({'results': results})

@login_required
def print_receipt(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related('student', 'installment', 'created_by'), 
        pk=payment_id
    )
    
    remaining_installment = 0
    if payment.installment:
        remaining_installment = payment.installment.amount - (payment.installment.paid_amount or 0)
    
    context = {
        'payment': payment,
        'student': payment.student,
        'installment': payment.installment,
        'remaining_installment': remaining_installment,
        'company_name': 'معهد الجبل العالي للعلوم الطبية',
        'company_address': 'طرابلس - ليبيا',
        'company_phone': '091 123456789 ',
        'company_email': 'info@institute.gmail',
        'print_date': datetime.now().strftime('%Y/%m/%d %H:%M'),
        'receipt_word': f"إيصال رقم {payment.receipt_number}",
        'amount_words': number_to_words(payment.amount),
    }
    
    return render(request, 'print_receipt.html', context)


def number_to_words(number):
    """تحويل الرقم إلى كلمات عربية"""
    try:
        number = int(number)
    except:
        return ""
    
    if number == 0:
        return "صفر"
    
    ones = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة"]
    tens = ["", "عشرة", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
    hundreds = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"]
    
    categories = [
        (1000000, "مليون", "مليونان", "ملايين"),
        (1000, "ألف", "ألفان", "آلاف")
    ]
    
    def convert_less_than_thousand(n):
        """تحويل رقم أقل من 1000"""
        if n == 0:
            return ""
        
        result = ""
        h = n // 100
        if h > 0:
            result += hundreds[h] + " "
            n %= 100
        
        if n >= 10 and n <= 19:
            if n == 10:
                result += "عشرة"
            elif n == 11:
                result += "أحد عشر"
            elif n == 12:
                result += "اثنا عشر"
            elif n == 13:
                result += "ثلاثة عشر"
            elif n == 14:
                result += "أربعة عشر"
            elif n == 15:
                result += "خمسة عشر"
            elif n == 16:
                result += "ستة عشر"
            elif n == 17:
                result += "سبعة عشر"
            elif n == 18:
                result += "ثمانية عشر"
            elif n == 19:
                result += "تسعة عشر"
            return result.strip()
        
        t = n // 10
        if t > 0:
            result += tens[t] + " "
            n %= 10
        
        if n > 0:
            result += ones[n]
        
        return result.strip()
    
    result = ""
    for value, singular, dual, plural in categories:
        if number >= value:
            count = number // value
            if count == 1:
                result += singular
            elif count == 2:
                result += dual
            elif count >= 3 and count <= 10:
                result += convert_less_than_thousand(count) + " " + plural
            else:
                result += convert_less_than_thousand(count) + " " + singular
            result += " "
            number %= value
    
    if number > 0:
        result += convert_less_than_thousand(number)
    
    return result.strip() + " دينار ليبي فقط"



@login_required
def finance(request):
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    semester_filter = request.GET.get('semester', '')
    tab = request.GET.get('tab', 'installments')
    
    installments = StudentInstallment.objects.select_related('student', 'semester').order_by('due_date')
    
    if search_query and tab == 'installments':
        installments = installments.filter(
            Q(student__full_name__icontains=search_query) |
            Q(student__registration_number__icontains=search_query)
        )
    
    if status_filter:
        installments = installments.filter(status=status_filter)
    
    if semester_filter:
        installments = installments.filter(semester_id=semester_filter)
    
    payments = Payment.objects.select_related('student', 'installment').order_by('-payment_date')[:30]
    
    semesters = AcademicSemester.objects.all().order_by('-start_date')
    
    context = {
        'installments': installments,
        'payments': payments,
        'status_filter': status_filter,
        'search_query': search_query,
        'semester_filter': semester_filter,
        'semesters': semesters,
        'current_tab': tab,
    }
    return render(request, 'finance.html', context)



@login_required
def installment_add(request):
    if request.method == 'POST':
        form = InstallmentForm(request.POST)
        if form.is_valid():
            installment = form.save(commit=False)
            installment.paid_amount = 0
            installment.status = 'pending'
            installment.save()
            
            student = installment.student
            student.update_total_fees()
            
            messages.success(request, 'تم إضافة القسط بنجاح')
            return redirect('finance')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج')
    else:
        form = InstallmentForm()
    
    return render(request, 'installment_form.html', {'form': form})


@login_required
def installment_payment_add(request, pk):
    installment = get_object_or_404(StudentInstallment, pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_date = form.cleaned_data['payment_date']
            payment_method = form.cleaned_data['payment_method']
            notes = form.cleaned_data.get('notes', '')
            
            if amount > installment.remaining_amount:
                messages.error(request, f'المبلغ المدخل ({amount}) يتجاوز المبلغ المتبقي للقسط ({installment.remaining_amount}) د.ل')
                return redirect('finance')
            
            payment = Payment.objects.create(
                student=installment.student,
                installment=installment,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                notes=notes,
                created_by=request.user
            )
            
            messages.success(request, f'تم تسجيل دفعة بقيمة {amount} دينار للقسط')
            return redirect('finance')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج')
    else:
        form = PaymentForm(initial={'student': installment.student, 'installment': installment})
    
    return render(request, 'payment_form.html', {
        'form': form,
        'installment': installment,
        'remaining_amount': installment.remaining_amount,
    })


@login_required
def student_print_card(request, pk):
    """طباعة بطاقة تعريف الطالب"""
    student = get_object_or_404(Student, pk=pk)
    
    context = {
        'student': student,
        'school_logo': settings.STATIC_URL + 'images/logo.png',
        'school_name': 'معهد الجبل العالي', 
    }
    return render(request, 'student_card_print.html', context)


@login_required
def student_bulk_cards(request):
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
    else:
        student_ids = request.GET.getlist('student_ids')
    
    if student_ids:
        students = Student.objects.filter(id__in=student_ids)
    else:
        students = Student.objects.all()[:20]
    
    context = {
        'students': students,
        'school_logo': settings.STATIC_URL + 'images/logo.png',
        'school_name': 'معهد الجبل العالي',
        'print_date': timezone.now(),
    }
    return render(request, 'student_bulk_cards_print.html', context)



def ar(text):
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)

def generate_student_pdf(student):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="student_card_{student.registration_number}.pdf"'
    )

    card_width = 85 * mm
    card_height = 54 * mm

    p = canvas.Canvas(response, pagesize=(card_width, card_height))
    width, height = card_width, card_height

    arabic_font = 'Helvetica'

    try:
        font_path = os.path.join(
            settings.BASE_DIR,
            'static',
            'fonts',
            'Amiri-Regular.ttf'
        )

        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
            arabic_font = 'ArabicFont'
    except:
        pass
    p.setFillColor(HexColor("#ffffff"))
    p.roundRect(0, 0, width, height, 4 * mm, fill=1)
    p.setStrokeColor(HexColor("#d90429"))
    p.setLineWidth(1)
    p.roundRect(1, 1, width - 2, height - 2, 4 * mm)
    p.setFillColor(HexColor("#d90429"))
    p.rect(0, height - 14 * mm, width, 14 * mm, fill=1)
    p.setFillColor(white)
    p.setFont(arabic_font, 11)
    p.drawCentredString(
        width / 2,
        height - 8 * mm,
        ar(settings.SITE_NAME)
    )
    p.setFont(arabic_font, 8)
    p.drawCentredString(
        width / 2,
        height - 12 * mm,
        ar("بطاقة طالب")
    )
    photo_width = 22 * mm
    photo_height = 22 * mm
    photo_x = width - 28 * mm
    photo_y = 14 * mm
    if student.photo and student.photo.path and os.path.exists(student.photo.path):
        try:
            p.drawImage(
                student.photo.path,
                photo_x,
                photo_y,
                width=photo_width,
                height=photo_height,
                preserveAspectRatio=True,
                mask='auto'
            )
        except:
            p.setFillColor(HexColor("#dddddd"))
            p.rect(photo_x, photo_y, photo_width, photo_height, fill=1)
            p.setFillColor(HexColor("#999999"))
            p.setFont(arabic_font, 10)
            p.drawCentredString(
                photo_x + photo_width / 2,
                photo_y + photo_height / 2 - 2,
                ar("صورة")
            )
    else:
        p.setFillColor(HexColor("#dddddd"))
        p.rect(photo_x, photo_y, photo_width, photo_height, fill=1)

        p.setFillColor(HexColor("#999999"))
        p.setFont(arabic_font, 10)

        p.drawCentredString(
            photo_x + photo_width / 2,
            photo_y + photo_height / 2 - 2,
            ar("صورة")
        )
    label_x = width - 58 * mm
    value_x = width - 34 * mm
    start_y = height - 20 * mm
    line_space = 5 * mm
    data = [
        ("الاسم", student.full_name),
        ("رقم القيد", student.registration_number),
        ("رقم الجلوس", str(student.id)),
        ("القسم", student.department.name if student.department else "-"),
        ("التخصص", student.specialization.name if student.specialization else "-"),
    ]

    for i, (label, value) in enumerate(data):
        y = start_y - (i * line_space)


        p.setFillColor(HexColor("#111111"))
        p.setFont(arabic_font, 8)
        p.drawRightString(
            value_x,
            y,
            ar(str(value))
        )
        p.setFillColor(HexColor("#111111"))
        p.setFont(arabic_font, 8)
        p.drawRightString(
            label_x,
            y,
            ar(label + ":")
        )
    
    p.save()
    return response

@login_required
def send_whatsapp_pdf(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if not student.phone:
        return JsonResponse({
            'error': 'عذراً، لا يوجد رقم هاتف مسجل لهذا الطالب'
        }, status=400)
    
    pdf_response = generate_student_pdf(student)
    
    if not pdf_response or pdf_response.status_code != 200:
        return JsonResponse({
            'error': 'حدث خطأ في إنشاء ملف PDF'
        }, status=500)
    
    pdf_filename = f"student_card_{student.registration_number}.pdf"
    pdf_path = default_storage.save(f'temp/{pdf_filename}', ContentFile(pdf_response.content))
    pdf_url = request.build_absolute_uri(f'/media/{pdf_path}')
    
    phone = student.phone.strip().replace(' ', '').replace('-', '')
    if phone.startswith('0'):
        phone = phone[1:]
    if not phone.startswith('218'):
        phone = '218' + phone
    
    message = f"""{settings.SITE_NAME}
    
 بطاقة الطالب الرسمي

 الاسم: {student.full_name}
 رقم القيد: {student.registration_number}
 القسم: {student.department.name if student.department else '-'}

لتحميل البطاقة بصيغة PDF:
{pdf_url}

يمكنك طباعة البطاقة أو حفظها على جهازك."""
    
    from urllib.parse import quote
    encoded_message = quote(message)
    
    whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    
    return JsonResponse({
        'success': True,
        'whatsapp_url': whatsapp_url,
        'pdf_url': pdf_url,
        'phone': phone
    })



@login_required
def expense_list(request):
    qs = Expense.objects.select_related('category').order_by('-expense_date')
    cat = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if cat:
        qs = qs.filter(category_id=cat)
    if date_from:
        qs = qs.filter(expense_date__gte=date_from)
    if date_to:
        qs = qs.filter(expense_date__lte=date_to)
    
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    expenses = paginator.get_page(page_number)
    
    total = qs.aggregate(t=Sum('amount'))['t'] or 0
    
    context = {
        'expenses': expenses,
        'categories': ExpenseCategory.objects.all(),
        'selected_category': cat,
        'date_from': date_from,
        'date_to': date_to,
        'total_amount': total,
    }
    return render(request, 'expense_list.html', context)


@login_required
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, 'تم تسجيل المصروف بنجاح')
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expense_form.html', {'form': form})


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المصروف')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expense_form.html', {'form': form})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'تم حذف المصروف')
        return redirect('expense_list')
    return render(request, 'confirm_delete.html', {'object': expense})


@login_required
def expense_category_list(request):
    categories = ExpenseCategory.objects.all()
    return render(request, 'expense_category_list.html', {'categories': categories})


@login_required
def expense_category_add(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الفئة')
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm()
    return render(request, 'expense_category_form.html', {'form': form})


@login_required
def reports(request):
    return render(request, 'reports.html')



@login_required
def financial_report(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    payments = Payment.objects.select_related('student')
    if date_from:
        payments = payments.filter(payment_date__gte=date_from)
    if date_to:
        payments = payments.filter(payment_date__lte=date_to)
    total_revenue_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    expenses = Expense.objects.select_related('category')
    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)
    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    installments = StudentInstallment.objects.all()
    if date_from:
        installments = installments.filter(due_date__gte=date_from)
    if date_to:
        installments = installments.filter(due_date__lte=date_to)
    
    total_revenue_due = installments.aggregate(total=Sum('amount'))['total'] or 0
    
    paid_from_due = Payment.objects.filter(
        installment__in=installments
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_unpaid = total_revenue_due - paid_from_due
    
    net_profit = total_revenue_paid - total_expenses
    
    collection_rate = (total_revenue_paid / total_revenue_due * 100) if total_revenue_due > 0 else 0
    
    context = {
        'total_revenue_paid': total_revenue_paid,
        'total_revenue_due': total_revenue_due,
        'total_unpaid': total_unpaid,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'collection_rate': collection_rate,
        'payments': payments,  
        'expenses': expenses,  
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'financial_report.html', context)

@login_required
def debts_report(request):
    search_query = request.GET.get('search', '')
    students = Student.objects.select_related('department').prefetch_related('payments', 'installments')
    
    if search_query:
        students = students.filter(
            Q(full_name__icontains=search_query) |
            Q(registration_number__icontains=search_query)
        )
    
    debtors = []
    for s in students:
        balance = s.balance
        if balance > 0:  
            overdue = s.installments.filter(status='overdue').count()
            debtors.append({
                'student': s,
                'total_fees': s.total_fees,
                'total_paid': s.total_paid,
                'balance': balance,
                'balance_raw': balance,
                'overdue_count': overdue,
            })
    
    debtors.sort(key=lambda x: x['balance_raw'], reverse=True)
    
    total_debt = sum(d['balance_raw'] for d in debtors)
    
    context = {
        'debtors': debtors,
        'total_debt': total_debt,
        'search_query': search_query,  
    }
    return render(request, 'debts_report.html', context)


@login_required
def students_report(request):
    total = Student.objects.count()
    
    by_department = Department.objects.annotate(
        cnt=Count('students')
    ).filter(cnt__gt=0).order_by('-cnt')
    
    by_specialization = Specialization.objects.annotate(
        cnt=Count('student')
    ).filter(cnt__gt=0).order_by('-cnt')
    
    departments_count = Department.objects.count()
    specializations_count = Specialization.objects.count()
    
    context = {
        'total': total,
        'by_department': by_department,
        'by_specialization': by_specialization,
        'departments_count': departments_count,
        'specializations_count': specializations_count,
    }
    return render(request, 'students_report.html', context)




@login_required
def print_students_report(request):
    department_id = request.GET.get('department', '')
    selected_fields = request.GET.getlist('fields', [])
    if request.method == 'POST':
        department_id = request.POST.get('department', '')
        selected_fields = request.POST.getlist('fields', [])
        students = Student.objects.select_related('department', 'specialization')
        
        if department_id and department_id != '':
            students = students.filter(department_id=department_id)
        else:
            students = students.all()
        
        students = students.order_by('registration_number')
        students_data = []
        for student in students:
            total_paid = Payment.objects.filter(student=student).aggregate(Sum('amount'))['amount__sum'] or 0           
            total_installments = StudentInstallment.objects.filter(student=student).aggregate(Sum('amount'))['amount__sum'] or 0
            remaining = total_installments - total_paid if total_installments > 0 else 0            
            students_data.append({
                'id': student.id,
                'full_name': student.full_name,
                'father_name': student.father_name,
                'registration_number': student.registration_number,
                'nation_number': student.nation_number,
                'phone': student.phone or '-',
                'department': student.department.name if student.department else '-',
                'specialization': student.specialization.name if student.specialization else '-',
                'status': student.get_status_display_ar(),
                'total_paid': total_paid,
                'remaining': remaining,
                'total_fees': total_installments,
            })
        
        department_name = "جميع طلبة المعهد"
        if department_id and department_id != '':
            dept = Department.objects.filter(id=department_id).first()
            if dept:
                department_name = f"طلبة قسم {dept.name}"
        
        context = {
            'students': students_data,
            'selected_fields': selected_fields,
            'department_name': department_name,
            'print_date': datetime.now(),
            'total_count': len(students_data),
        }
        
        return render(request, 'students_report_print.html', context)
    
    departments = Department.objects.all().order_by('name')
    fields = [
        {'value': 'full_name', 'label': 'اسم الطالب', 'checked': True},
        {'value': 'registration_number', 'label': 'رقم القيد', 'checked': True},
        {'value': 'id', 'label': 'رقم الجلوس', 'checked': True},
        {'value': 'phone', 'label': 'رقم الهاتف', 'checked': False},
        {'value': 'department', 'label': 'القسم', 'checked': True},
        {'value': 'specialization', 'label': 'التخصص', 'checked': False},
        {'value': 'total_paid', 'label': 'المدفوعات', 'checked': True},
        {'value': 'remaining', 'label': 'الدين المتبقي', 'checked': True},
    ]
    
    context = {
        'departments': departments,
        'fields': fields,
        'department_id': department_id,
        'selected_fields': selected_fields,
    }
    return render(request, 'students_report_form.html', context)






@login_required
def dashboard(request):
    today = date.today()
    this_month_start = today.replace(day=1)

    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='active').count()
    new_this_month = Student.objects.filter(created_at__gte=this_month_start).count()

    total_revenue = Payment.objects.aggregate(t=Sum('amount'))['t'] or 0
    revenue_this_month = Payment.objects.filter(
        payment_date__gte=this_month_start
    ).aggregate(t=Sum('amount'))['t'] or 0

    total_expenses = Expense.objects.aggregate(t=Sum('amount'))['t'] or 0
    expenses_this_month = Expense.objects.filter(
        expense_date__gte=this_month_start
    ).aggregate(t=Sum('amount'))['t'] or 0

    overdue_qs = StudentInstallment.objects.filter(status='overdue')
    overdue_count = overdue_qs.count()
    overdue_amount = overdue_qs.aggregate(t=Sum('amount'))['t'] or 0

    monthly_data = []
    for i in range(5, -1, -1):
        d = today - timedelta(days=30 * i)
        m_start = d.replace(day=1)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1)
        rev = Payment.objects.filter(
            payment_date__gte=m_start, payment_date__lt=m_end
        ).aggregate(t=Sum('amount'))['t'] or 0
        exp = Expense.objects.filter(
            expense_date__gte=m_start, expense_date__lt=m_end
        ).aggregate(t=Sum('amount'))['t'] or 0
        month_names = ['يناير','فبراير','مارس','أبريل','مايو','يونيو',
                       'يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']
        monthly_data.append({
            'month': month_names[m_start.month - 1],
            'revenue': int(rev),
            'expenses': int(exp),
        })

    dept_breakdown = Department.objects.annotate(
        cnt=Count('students')
    ).filter(cnt__gt=0).values('name', 'cnt')

    recent_payments = Payment.objects.select_related('student').order_by('-payment_date')[:5]
    overdue_installments = StudentInstallment.objects.filter(
        status='overdue'
    ).select_related('student').order_by('due_date')[:5]

    context = {
        'total_students': total_students,
        'active_students': active_students,
        'new_this_month': new_this_month,
        'total_revenue': total_revenue,
        'revenue_this_month': revenue_this_month,
        'total_expenses': total_expenses,
        'expenses_this_month': expenses_this_month,
        'net_profit': total_revenue - total_expenses,
        'overdue_count': overdue_count,
        'overdue_amount': overdue_amount,
        'monthly_data': monthly_data,
        'dept_breakdown': list(dept_breakdown),
        'recent_payments': recent_payments,
        'overdue_installments': overdue_installments,
    }
    return render(request, 'dashboard.html', context)



@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})

@login_required
def employee_create(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        position = request.POST.get('position')
        phone = request.POST.get('phone')
        payment_type = request.POST.get('payment_type')
        monthly_salary = request.POST.get('monthly_salary', 0)
        hourly_rate = request.POST.get('hourly_rate', 0)
        
        employee = Employee(
            full_name=full_name,
            position=position,
            phone=phone,
            payment_type=payment_type,
            monthly_salary=monthly_salary,
            hourly_rate=hourly_rate
        )
        employee.save()
        messages.success(request, f'تم إضافة الموظف {full_name} بنجاح')
        return redirect('employee_list')
    
    return render(request, 'employee_form.html', {'title': 'إضافة موظف جديد'})

@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.full_name = request.POST.get('full_name')
        employee.position = request.POST.get('position')
        employee.phone = request.POST.get('phone')
        employee.payment_type = request.POST.get('payment_type')
        employee.monthly_salary = request.POST.get('monthly_salary', 0)
        employee.hourly_rate = request.POST.get('hourly_rate', 0)
        employee.status = request.POST.get('status')
        employee.save()
        messages.success(request, f'تم تعديل بيانات {employee.full_name}')
        return redirect('employee_list')
    
    return render(request, 'employee_form.html', {'employee': employee, 'title': 'تعديل بيانات موظف'})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'تم حذف الموظف بنجاح')
        return redirect('employee_list')
    return render(request, 'employee_confirm_delete.html', {'employee': employee})

@login_required
def absence_create(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        absence_date = request.POST.get('absence_date')
        deduction_amount = request.POST.get('deduction_amount')
        reason = request.POST.get('reason')
        
        employee = get_object_or_404(Employee, pk=employee_id)
        
        AbsenceRecord.objects.create(
            employee=employee,
            absence_date=absence_date,
            deduction_amount=deduction_amount,
            reason=reason
        )
        messages.success(request, f'تم تسجيل غياب {employee.full_name} بتاريخ {absence_date}')
        return redirect('absence_list')
    
    employees = Employee.objects.filter(payment_type='monthly', status='active')
    return render(request, 'absence_form.html', {'employees': employees, 'title': 'تسجيل غياب'})

@login_required
def absence_list(request):
    absences = AbsenceRecord.objects.all().select_related('employee')
    return render(request, 'absence_list.html', {'absences': absences})

@login_required
def absence_delete(request, pk):
    absence = get_object_or_404(AbsenceRecord, pk=pk)
    if request.method == 'POST':
        absence.delete()
        messages.success(request, 'تم حذف تسجيل الغياب')
        return redirect('absence_list')
    return render(request, 'absence_confirm_delete.html', {'absence': absence})

@login_required
def monthly_salary_payment(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id, payment_type='monthly')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes')
        
        payment = MonthlySalaryPayment(
            employee=employee,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            notes=notes,
            created_by=request.user
        )
        payment.save()
        messages.success(request, f'تم تسديد {amount} ل.س للموظف {employee.full_name}')
        return redirect('employee_list')
    
    return render(request, 'monthly_payment_form.html', {'employee': employee})

@login_required
def monthly_salary_statement(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id, payment_type='monthly')
    absences = AbsenceRecord.objects.filter(employee=employee)
    payments = MonthlySalaryPayment.objects.filter(employee=employee)
    
    total_deductions = absences.aggregate(total=Sum('deduction_amount'))['total'] or 0
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    net_salary = employee.monthly_salary - total_deductions
    remaining = net_salary - total_paid
    
    context = {
        'employee': employee,
        'absences': absences,
        'payments': payments,
        'total_deductions': total_deductions,
        'total_paid': total_paid,
        'net_salary': net_salary,
        'remaining': remaining,
    }
    return render(request, 'monthly_statement.html', context)

@login_required
def hourly_work_create(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        work_date = request.POST.get('work_date')
        hours = request.POST.get('hours')
        notes = request.POST.get('notes')
        
        employee = get_object_or_404(Employee, pk=employee_id, payment_type='hourly')
        
        work_record = HourlyWorkRecord(
            employee=employee,
            work_date=work_date,
            hours=hours,
            notes=notes
        )
        work_record.save()
        messages.success(request, f'تم تسجيل {hours} ساعات للموظف {employee.full_name}')
        return redirect('hourly_work_list')
    
    employees = Employee.objects.filter(payment_type='hourly', status='active')
    return render(request, 'hourly_work_form.html', {'employees': employees, 'title': 'تسجيل ساعات عمل'})

@login_required
def hourly_work_list(request):
    work_records = HourlyWorkRecord.objects.all().select_related('employee')
    return render(request, 'hourly_work_list.html', {'work_records': work_records})

@login_required
def hourly_work_delete(request, pk):
    work_record = get_object_or_404(HourlyWorkRecord, pk=pk)
    if request.method == 'POST':
        work_record.delete()
        messages.success(request, 'تم حذف سجل ساعات العمل')
        return redirect('hourly_work_list')
    return render(request, 'hourly_work_confirm_delete.html', {'work_record': work_record})

@login_required
def hourly_payment_create(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id, payment_type='hourly')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes')
        
        payment = HourlyPayment(
            employee=employee,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            notes=notes,
            created_by=request.user
        )
        payment.save()
        messages.success(request, f'تم تسديد {amount} ل.س للموظف {employee.full_name}')
        return redirect('employee_list')
    
    unpaid_total = HourlyWorkRecord.objects.filter(employee=employee, is_paid=False).aggregate(total=Sum('total_amount'))['total'] or 0
    
    return render(request, 'hourly_payment_form.html', {
        'employee': employee,
        'unpaid_total': unpaid_total
    })

@login_required
def hourly_statement(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id, payment_type='hourly')
    work_records = HourlyWorkRecord.objects.filter(employee=employee)
    payments = HourlyPayment.objects.filter(employee=employee)
    
    total_hours = work_records.aggregate(total=Sum('hours'))['total'] or 0
    total_earned = work_records.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    remaining = total_earned - total_paid
    
    context = {
        'employee': employee,
        'work_records': work_records,
        'payments': payments,
        'total_hours': total_hours,
        'total_earned': total_earned,
        'total_paid': total_paid,
        'remaining': remaining,
    }
    return render(request, 'hourly_statement.html', context)

@login_required
def hr_dashboard(request):
    monthly_employees = Employee.objects.filter(payment_type='monthly', status='active')
    hourly_employees = Employee.objects.filter(payment_type='hourly', status='active')
    
    monthly_total_salary = sum(emp.monthly_salary for emp in monthly_employees)
    monthly_total_deductions = sum(emp.total_absence_deductions for emp in monthly_employees)
    monthly_total_paid = sum(emp.total_monthly_paid for emp in monthly_employees)
    monthly_net = monthly_total_salary - monthly_total_deductions
    monthly_remaining = monthly_net - monthly_total_paid
    
    hourly_total_earned = sum(emp.total_hourly_earned for emp in hourly_employees)
    hourly_total_paid = sum(emp.total_hourly_paid for emp in hourly_employees)
    hourly_remaining = hourly_total_earned - hourly_total_paid
    
    context = {
        'monthly_count': monthly_employees.count(),
        'hourly_count': hourly_employees.count(),
        'monthly_total_salary': monthly_total_salary,
        'monthly_total_deductions': monthly_total_deductions,
        'monthly_net': monthly_net,
        'monthly_remaining': monthly_remaining,
        'hourly_total_earned': hourly_total_earned,
        'hourly_remaining': hourly_remaining,
    }
    return render(request, 'hr_dashboard.html', context)