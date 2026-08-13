from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q, Case, When, FloatField
from django.contrib import messages
from faculty.models import Faculty
from students.models import Course, Enrollment, Student, Program


@login_required
def faculty_dashboard(request):
    try:
        faculty = Faculty.objects.get(user=request.user, is_active=True)
    except Faculty.DoesNotExist:
        faculty = None

    if not faculty:
        context = {'faculty': None}
        return render(request, 'dashboard/faculty.html', context)

    courses = Course.objects.filter(faculty=faculty, is_active=True).prefetch_related('programs').annotate(
        student_count=Count('enrollments', filter=Q(enrollments__status__in=['ENROLLED', 'IN_PROGRESS'])),
        completed_count=Count('enrollments', filter=Q(enrollments__status='COMPLETED')),
    )

    pending_grades = Enrollment.objects.filter(
        course__faculty=faculty,
        status='IN_PROGRESS'
    ).select_related('student', 'course').order_by('-created_at')[:20]

    total_students = courses.aggregate(total=Count('enrollments', distinct=True, filter=Q(enrollments__status__in=['ENROLLED', 'IN_PROGRESS'])))['total'] or 0

    program_performance = Program.objects.filter(
        courses__faculty=faculty,
        is_active=True
    ).annotate(
        avg_grade=Avg('students__enrollments__percentage', filter=Q(students__enrollments__status='COMPLETED', students__enrollments__percentage__isnull=False)),
        student_count=Count('students', filter=Q(students__is_active=True), distinct=True),
    ).distinct()

    context = {
        'faculty': faculty,
        'courses': courses,
        'pending_grades': pending_grades,
        'total_students': total_students,
        'program_performance': program_performance,
    }
    return render(request, 'dashboard/faculty.html', context)


@login_required
def faculty_courses(request):
    try:
        faculty = Faculty.objects.get(user=request.user, is_active=True)
    except Faculty.DoesNotExist:
        faculty = None
    context = {
        'faculty': faculty,
        'courses': Course.objects.filter(faculty=faculty, is_active=True).select_related('faculty').prefetch_related('programs') if faculty else [],
    }
    return render(request, 'courses/list.html', context)


@login_required
def faculty_grades(request):
    try:
        faculty = Faculty.objects.get(user=request.user, is_active=True)
    except Faculty.DoesNotExist:
        faculty = None

    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        letter_grade = request.POST.get('letter_grade', '')
        percentage = request.POST.get('percentage', '')

        if enrollment_id:
            enrollment = get_object_or_404(Enrollment, id=enrollment_id, course__faculty=faculty)
            enrollment.letter_grade = letter_grade
            if percentage:
                enrollment.percentage = float(percentage)
            enrollment.save()
            messages.success(request, f'Grade updated for {enrollment.student.get_full_name()}')
            return redirect('faculty:grades')

    enrollments = Enrollment.objects.filter(
        course__faculty=faculty,
        status='IN_PROGRESS'
    ).select_related('student', 'course').order_by('-created_at')[:50]

    context = {
        'faculty': faculty,
        'enrollments': enrollments,
    }
    return render(request, 'portal/faculty_grades.html', context)
