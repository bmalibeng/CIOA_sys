from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q, Avg, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta, date
from django.http import HttpResponse, JsonResponse
from students.models import Student, Program, Cohort, Payment, Enrollment, Course
from faculty.models import Faculty
from core.models import User, SiteSettings
from decimal import Decimal
from portal.utils.pdf_receipt import generate_payment_receipt


def is_admin(user):
    return user.is_authenticated and user.user_type == 'ADMIN'


def is_faculty(user):
    return user.is_authenticated and user.user_type == 'FACULTY'


def is_student(user):
    return user.is_authenticated and user.user_type == 'STUDENT'


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    settings = SiteSettings.get_solo()
    context = {
        'hero_bg_image': settings.hero_background.url if settings.hero_background else None,
    }
    return render(request, 'landing.html', context)


@login_required
def dashboard_redirect(request):
    if request.user.user_type == 'STUDENT':
        return redirect('students:dashboard')
    elif request.user.user_type == 'FACULTY':
        return redirect('faculty:dashboard')
    else:
        return redirect('portal:admin_dashboard')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_students = Student.objects.filter(is_active=True).count()
    active_cohorts = Cohort.objects.filter(is_active=True).count()
    pending_payments = Payment.objects.filter(status='PENDING').count()
    total_revenue = Payment.objects.filter(status='VERIFIED').aggregate(total=Sum('amount'))['total'] or 0
    monthly_revenue = Payment.objects.filter(
        status='VERIFIED',
        payment_date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_faculty = Faculty.objects.filter(is_active=True).count()
    total_programs = Program.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()

    upcoming_graduates = Student.objects.filter(
        is_active=True,
        expected_graduation_date__gte=today,
        expected_graduation_date__lte=today + timedelta(days=90)
    ).select_related('program', 'cohort').order_by('expected_graduation_date')[:10]

    for student in upcoming_graduates:
        student.days_to_graduation = (student.expected_graduation_date - today).days

    program_stats = Program.objects.filter(is_active=True).annotate(
        student_count=Count('students', filter=Q(students__is_active=True)),
        revenue=Sum('payments__amount', filter=Q(payments__status='VERIFIED'))
    )

    recent_students = Student.objects.filter(is_active=True).order_by('-created_at')[:10]
    recent_payments = Payment.objects.select_related('student', 'program').order_by('-created_at')[:10]
    pending_payment_list = Payment.objects.filter(status='PENDING').select_related('student', 'program')[:10]

    context = {
        'total_students': total_students,
        'active_cohorts': active_cohorts,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_faculty': total_faculty,
        'total_programs': total_programs,
        'total_courses': total_courses,
        'recent_students': recent_students,
        'recent_payments': recent_payments,
        'pending_payment_list': pending_payment_list,
        'upcoming_graduates': upcoming_graduates,
        'program_stats': program_stats,
    }
    return render(request, 'dashboard/admin.html', context)


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.all().order_by('-created_at')
    context = {
        'users': users,
    }
    return render(request, 'admin_pages/manage_users.html', context)


@login_required
@user_passes_test(is_admin)
def add_user(request):
    from django.contrib import messages
    from django.shortcuts import redirect
    from students.models import Student, Program, Cohort
    programs = Program.objects.filter(is_active=True)
    cohorts = Cohort.objects.filter(is_active=True)
    if request.method == 'POST':
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        if email and user_type and password:
            user = User.objects.create_user(
                email=email,
                password=password,
                user_type=user_type,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
            )
            if user_type == 'FACULTY':
                faculty_id = request.POST.get('faculty_id', '')
                department = request.POST.get('department', '')
                if faculty_id:
                    Faculty.objects.create(
                        user=user,
                        faculty_id=faculty_id,
                        department=department,
                    )
            elif user_type == 'STUDENT':
                student_id = request.POST.get('student_id', '')
                program_id = request.POST.get('program')
                cohort_id = request.POST.get('cohort')
                enrollment_date = request.POST.get('enrollment_date')
                expected_graduation_date = request.POST.get('expected_graduation_date')
                if student_id and program_id and cohort_id and enrollment_date and expected_graduation_date:
                    Student.objects.create(
                        user=user,
                        student_id=student_id,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=phone,
                        program_id=program_id,
                        cohort_id=cohort_id,
                        enrollment_date=enrollment_date,
                        expected_graduation_date=expected_graduation_date,
                    )
            messages.success(request, f'User {email} created successfully.')
            return redirect('portal:manage_users')
        messages.error(request, 'Please fill all required fields.')
    return render(request, 'admin_pages/user_form.html', {
        'form_user': None,
        'programs': programs,
        'cohorts': cohorts,
    })


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    from django.contrib import messages
    from django.shortcuts import redirect
    from students.models import Student, Program, Cohort
    user = get_object_or_404(User, id=user_id)
    programs = Program.objects.filter(is_active=True)
    cohorts = Cohort.objects.filter(is_active=True)
    student_profile = getattr(user, 'student_profile', None)
    faculty_profile = getattr(user, 'faculty_profile', None)
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.user_type = request.POST.get('user_type', user.user_type)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        user.save()

        if user.user_type == 'STUDENT':
            student_id = request.POST.get('student_id', '')
            program_id = request.POST.get('program')
            cohort_id = request.POST.get('cohort')
            enrollment_date = request.POST.get('enrollment_date')
            expected_graduation_date = request.POST.get('expected_graduation_date')
            if student_profile:
                student_profile.student_id = student_id or student_profile.student_id
                student_profile.first_name = user.first_name
                student_profile.last_name = user.last_name
                student_profile.email = user.email
                student_profile.phone = user.phone
                if program_id:
                    student_profile.program_id = program_id
                if cohort_id:
                    student_profile.cohort_id = cohort_id
                if enrollment_date:
                    student_profile.enrollment_date = enrollment_date
                if expected_graduation_date:
                    student_profile.expected_graduation_date = expected_graduation_date
                student_profile.save()
            elif student_id and program_id and cohort_id and enrollment_date and expected_graduation_date:
                Student.objects.create(
                    user=user,
                    student_id=student_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone=user.phone,
                    program_id=program_id,
                    cohort_id=cohort_id,
                    enrollment_date=enrollment_date,
                    expected_graduation_date=expected_graduation_date,
                )
        elif user.user_type == 'FACULTY':
            try:
                faculty = user.faculty_profile
                faculty.faculty_id = request.POST.get('faculty_id', faculty.faculty_id)
                faculty.department = request.POST.get('department', faculty.department)
                faculty.save()
            except Faculty.DoesNotExist:
                faculty_id = request.POST.get('faculty_id', '')
                department = request.POST.get('department', '')
                if faculty_id:
                    Faculty.objects.create(user=user, faculty_id=faculty_id, department=department)
        messages.success(request, f'User {user.email} updated successfully.')
        return redirect('portal:manage_users')
    return render(request, 'admin_pages/user_form.html', {
        'form_user': user,
        'is_faculty': user.user_type == 'FACULTY',
        'faculty_profile': faculty_profile,
        'student_profile': student_profile,
        'programs': programs,
        'cohorts': cohorts,
    })


@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    from django.contrib import messages
    from django.shortcuts import redirect
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            messages.error(request, 'You cannot delete your own account.')
        else:
            email = user.email
            user.is_active = False
            user.save()
            messages.success(request, f'User {email} deactivated successfully.')
    return redirect('portal:manage_users')


@login_required
@user_passes_test(is_admin)
def grade_monitoring(request):
    from django.db.models import Avg, Case, When, FloatField
    students = Student.objects.filter(is_active=True).select_related('program', 'cohort').prefetch_related('enrollments__course')
    student_data = []
    for student in students:
        enrollments = student.enrollments.all()
        completed_enrollments = [e for e in enrollments if e.status == 'COMPLETED' and e.percentage is not None]
        avg_percentage = sum(e.percentage for e in completed_enrollments) / len(completed_enrollments) if completed_enrollments else None
        student_data.append({
            'student': student,
            'enrollments': enrollments,
            'completed_count': len(completed_enrollments),
            'avg_percentage': avg_percentage,
        })

    program_avg = Program.objects.filter(is_active=True).annotate(
        avg_grade=Avg(
            'students__enrollments__percentage',
            filter=Q(students__enrollments__status='COMPLETED', students__enrollments__percentage__isnull=False, students__is_active=True)
        )
    )

    context = {
        'student_grades': student_data,
        'program_avg': program_avg,
    }
    return render(request, 'admin_pages/grade_monitoring.html', context)


@login_required
@user_passes_test(is_admin)
def graduation_tracking(request):
    today = timezone.now().date()
    upcoming = Student.objects.filter(
        is_active=True,
        expected_graduation_date__gte=today,
        expected_graduation_date__lte=today + timedelta(days=180)
    ).select_related('program', 'cohort').order_by('expected_graduation_date')

    past_graduates = Student.objects.filter(
        is_active=True,
        status='GRADUATED'
    ).select_related('program', 'cohort').order_by('-actual_graduation_date')[:50]

    context = {
        'upcoming_graduates': upcoming,
        'past_graduates': past_graduates,
        'today': today,
    }
    return render(request, 'admin_pages/graduation_tracking.html', context)


@login_required
@user_passes_test(is_admin)
def import_excel(request):
    from django.contrib import messages
    from django.shortcuts import redirect
    if request.method == 'POST' and request.FILES.get('excel_file'):
        messages.info(request, 'Excel import functionality requires openpyxl package.')
    return render(request, 'admin_pages/import.html')


@login_required
@user_passes_test(is_admin)
def record_payment(request):
    from django.contrib import messages
    from django.shortcuts import redirect
    students = Student.objects.filter(is_active=True).select_related('program', 'cohort').order_by('first_name', 'last_name')
    programs = Program.objects.filter(is_active=True)

    if request.method == 'POST':
        student_id = request.POST.get('student')
        program_id = request.POST.get('program')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        notes = request.POST.get('notes', '')

        if student_id and program_id and amount and payment_date:
            try:
                student = Student.objects.get(id=student_id, is_active=True)
                program = Program.objects.get(id=program_id, is_active=True)
                amount_decimal = Decimal(amount)
                payment = Payment.objects.create(
                    student=student,
                    program=program,
                    amount=amount_decimal,
                    payment_date=payment_date,
                    received_by=request.user,
                    status='PENDING',
                    notes=notes,
                )
                messages.success(request, f'Payment of M {amount_decimal:,.2f} recorded successfully. Receipt: {payment.receipt_number}')

                if 'generate_receipt' in request.POST:
                    buffer = generate_payment_receipt(payment)
                    response = HttpResponse(buffer, content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.receipt_number}.pdf"'
                    return response

                return redirect('portal:record_payment')
            except (Student.DoesNotExist, Program.DoesNotExist, ValueError) as e:
                messages.error(request, f'Error recording payment: {e}')
        else:
            messages.error(request, 'Please fill all required fields.')

    context = {
        'students': students,
        'programs': programs,
    }
    return render(request, 'admin_pages/record_payment.html', context)


@login_required
@user_passes_test(is_admin)
def get_student_balance(request, student_id):
    try:
        student = Student.objects.get(id=student_id, is_active=True)
        balance = student.get_balance_due()
        total_paid = student.get_total_paid()
        total_fees = student.program.total_fees
        return JsonResponse({
            'success': True,
            'total_fees': float(total_fees),
            'total_paid': float(total_paid),
            'balance_due': float(balance),
        })
    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Student not found'})


@login_required
@user_passes_test(is_admin)
def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    buffer = generate_payment_receipt(payment)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.receipt_number}.pdf"'
    return response


@login_required
@user_passes_test(is_admin)
def verify_payments(request):
    from django.contrib import messages
    from django.shortcuts import redirect
    if request.method == 'POST':
        action = request.POST.get('action')
        payment_ids = request.POST.getlist('payment_ids')
        if action == 'verify':
            Payment.objects.filter(id__in=payment_ids).update(status='VERIFIED')
            messages.success(request, f'{len(payment_ids)} payment(s) verified.')
        elif action == 'reject':
            Payment.objects.filter(id__in=payment_ids).update(status='REJECTED')
            messages.warning(request, f'{len(payment_ids)} payment(s) rejected.')
        return redirect('portal:verify_payments')
    context = {
        'pending_payments': Payment.objects.filter(status='PENDING').select_related('student', 'program', 'received_by'),
    }
    return render(request, 'admin_pages/verify_payments.html', context)


@login_required
@user_passes_test(is_admin)
def generate_reports(request):
    from django.contrib import messages
    report_type = request.GET.get('type', 'overview')
    context = {
        'report_type': report_type,
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_programs': Program.objects.filter(is_active=True).count(),
        'total_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_revenue': Payment.objects.filter(status='VERIFIED').aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'admin_pages/reports.html', context)


@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
    }
    if user.user_type == 'STUDENT':
        try:
            context['student'] = Student.objects.get(email=user.email, is_active=True)
        except Student.DoesNotExist:
            pass
    elif user.user_type == 'FACULTY':
        try:
            context['faculty'] = Faculty.objects.get(user=user, is_active=True)
        except Faculty.DoesNotExist:
            pass
    return render(request, 'profile.html', context)


@login_required
def course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk, is_active=True)
    except Course.DoesNotExist:
        from django.http import Http404
        raise Http404("Course not found")
    context = {
        'course': course,
    }
    return render(request, 'courses/detail.html', context)
