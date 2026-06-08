from django.urls import path
from .views import *


urlpatterns = [
    path('',dashboard,name='dashboard'),
    path('accounts/login/',user_login,name='user_login'),
    path('logout/',user_logout,name='logout'),

    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_add'),
    path('users/<int:pk>/update/', user_update, name='user_edit'),
    path('users/<int:pk>/delete/', user_delete, name='user_delete'),    

    path('departments/', department_list, name='department_list'),
    path('departments/add/', department_add, name='department_add'),
    path('departments/<int:pk>/edit/', department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', department_delete, name='department_delete'),
    path('specializations/add/', specialization_add, name='specialization_add'),
    path('specializations/<int:pk>/edit/', specialization_edit, name='specialization_edit'),
    path('specializations/<int:pk>/delete/', specialization_delete, name='specialization_delete'),

    path('semesters/', semester_list, name='semester_list'),
    path('semester/add/', semester_add, name='semester_add'),
    path('semester/<int:pk>/edit/', semester_edit, name='semester_edit'),
    path('semester/<int:pk>/delete/', semester_delete, name='semester_delete'),

    path('students/', student_list, name='student_list'),
    path('students/add/', student_add, name='student_add'),
    path('students/<int:pk>/', student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', student_delete, name='student_delete'),
    path('student/<int:pk>/print-card/', student_print_card, name='student_print_card'),
    path('send-whatsapp-pdf/<int:pk>/', send_whatsapp_pdf, name='send_whatsapp_pdf'),
    path('students/bulk-cards/', student_bulk_cards, name='student_bulk_cards'),

    path('finance/', finance, name='finance'),
    path('finance/payment/add/<int:pk>', installment_payment_add, name='payment_add'),
    path('finance/installment/add/', installment_add, name='installment_add'),
    path('print/receipt/<int:payment_id>/', print_receipt, name='print_receipt'),
    path('api/search-students/', search_students, name='search_students'),
    path('api/search-installments/', search_installments, name='search_installments'),
    path('finance/installment/edit/<int:pk>/', installment_edit, name='installment_edit'),
    path('finance/installment/delete/<int:pk>/', installment_delete, name='installment_delete'),

    path('expenses/',expense_list, name='expense_list'),
    path('expenses/add/',expense_add, name='expense_add'),
    path('expenses/<int:pk>/edit/',expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/',expense_delete, name='expense_delete'),
    path('expense-categories/',expense_category_list, name='expense_category_list'),
    path('expense-categories/add/',expense_category_add, name='expense_category_add'),

    path('reports/',reports, name='reports'),
    path('reports/financial/',financial_report, name='financial_report'),
    path('reports/debts/',debts_report, name='debts_report'),
    path('reports/students/',students_report, name='students_report'),
    path('reports/students/print/', print_students_report, name='students_report_print'),

    path('hr/dashboard/', dashboard_hr, name='hr_dashboard'),
    path('hr/employees/', employee_list, name='employee_list'),
    path('hr/employees/create/', employee_create, name='employee_create'),
    path('hr/employees/<int:pk>/edit/', employee_edit, name='employee_edit'),
    path('hr/attendance/', attendance_list, name='attendance_list'),
    path('hr/attendance/create/', attendance_create, name='attendance_create'),
    path('hr/payroll/', payroll_list, name='payroll_list'),
    path('hr/payroll/create/', payroll_create, name='payroll_create'),
    path('hr/payroll/<int:payroll_id>/pay/', payroll_payment_create, name='payroll_payment_create'),

]