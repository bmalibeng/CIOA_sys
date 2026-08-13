from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from students.models import Student, Enrollment, Payment


@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(email=request.user.email, is_active=True)
    except Student.DoesNotExist:
        student = None
    context = {
        'student': student,
        'remaining_months': student.get_remaining_months() if student else 0,
        'progress_percentage': student.get_progress_percentage() if student else 0,
        'balance_due': student.get_balance_due() if student else 0,
        'total_paid': student.get_total_paid() if student else 0,
        'enrollments': Enrollment.objects.filter(student=student).select_related('course')[:10] if student else [],
        'payments': Payment.objects.filter(student=student)[:10] if student else [],
    }
    return render(request, 'dashboard/student.html', context)


@login_required
def student_courses(request):
    try:
        student = Student.objects.get(email=request.user.email, is_active=True)
    except Student.DoesNotExist:
        student = None
    context = {
        'student': student,
        'enrollments': Enrollment.objects.filter(student=student).select_related('course') if student else [],
    }
    return render(request, 'courses/list.html', context)


@login_required
def student_payments(request):
    try:
        student = Student.objects.get(email=request.user.email, is_active=True)
    except Student.DoesNotExist:
        student = None
    context = {
        'student': student,
        'payments': Payment.objects.filter(student=student).select_related('program', 'received_by') if student else [],
        'balance_due': student.get_balance_due() if student else 0,
    }
    return render(request, 'portal/student_payments.html', context)
