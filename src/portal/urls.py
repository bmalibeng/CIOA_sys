from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('grades/', views.grade_monitoring, name='grade_monitoring'),
    path('graduates/', views.graduation_tracking, name='graduation_tracking'),
    path('import/', views.import_excel, name='import_excel'),
    path('payments/record/', views.record_payment, name='record_payment'),
    path('payments/student-balance/<int:student_id>/', views.get_student_balance, name='get_student_balance'),
    path('payments/verify/', views.verify_payments, name='verify_payments'),
    path('payments/receipt/<int:payment_id>/', views.download_receipt, name='download_receipt'),
    path('reports/', views.generate_reports, name='generate_reports'),
]
