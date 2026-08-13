from django.contrib import admin
from students.models import Program, Cohort, Student, Course, Enrollment, Payment
from django.http import HttpResponse
import csv
from django.utils import timezone


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'duration_months', 'total_fees', 'allows_installments', 'is_active')
    list_filter = ('is_active', 'allows_installments', 'created_at')
    search_fields = ('code', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'start_date', 'expected_end_date', 'max_students', 'is_active')
    list_filter = ('program', 'is_active', 'start_date')
    search_fields = ('name', 'program__code', 'program__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'program', 'cohort', 'status', 'enrollment_date', 'get_total_paid', 'get_balance_due', 'is_active')
    list_filter = ('program', 'cohort', 'status', 'is_active', 'enrollment_date')
    search_fields = ('student_id', 'first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'student_id', 'get_total_paid', 'get_balance_due')
    actions = ['export_students', 'mark_graduated', 'mark_withdrawn']

    def get_total_paid(self, obj):
        return f"M {obj.get_total_paid():,.2f}"
    get_total_paid.short_description = "Total Paid"

    def get_balance_due(self, obj):
        return f"M {obj.get_balance_due():,.2f}"
    get_balance_due.short_description = "Balance Due"

    def export_students(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Student ID', 'First Name', 'Last Name', 'Email', 'Phone',
            'Program', 'Cohort', 'Enrollment Date', 'Expected Graduation',
            'Status', 'Total Paid (M)', 'Balance Due (M)'
        ])
        for student in queryset.select_related('program', 'cohort'):
            writer.writerow([
                student.student_id,
                student.first_name,
                student.last_name,
                student.email,
                student.phone,
                student.program.name if student.program else '',
                student.cohort.name if student.cohort else '',
                student.enrollment_date,
                student.expected_graduation_date,
                student.status,
                student.get_total_paid(),
                student.get_balance_due(),
            ])
        return response
    export_students.short_description = "Export selected students to CSV"

    def mark_graduated(self, request, queryset):
        updated = queryset.update(status='GRADUATED', actual_graduation_date=timezone.now().date())
        self.message_user(request, f"{updated} students marked as graduated.")
    mark_graduated.short_description = "Mark selected students as graduated"

    def mark_withdrawn(self, request, queryset):
        updated = queryset.update(status='WITHDRAWN')
        self.message_user(request, f"{updated} students marked as withdrawn.")
    mark_withdrawn.short_description = "Mark selected students as withdrawn"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'credits', 'faculty', 'is_active')
    list_filter = ('is_active', 'credits', 'programs')
    search_fields = ('course_code', 'title')
    filter_horizontal = ('programs',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'enrollment_date', 'letter_grade')
    list_filter = ('status', 'enrollment_date', 'course__programs')
    search_fields = ('student__student_id', 'student__first_name', 'student__last_name', 'course__course_code', 'course__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'student', 'program', 'amount', 'payment_date', 'status', 'received_by')
    list_filter = ('status', 'payment_date', 'program')
    search_fields = ('receipt_number', 'student__student_id', 'student__first_name', 'student__last_name')
    readonly_fields = ('receipt_number', 'created_at', 'updated_at')
    actions = ['bulk_verify', 'bulk_reject']

    def bulk_verify(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='VERIFIED')
        self.message_user(request, f"{updated} payment(s) verified.")
    bulk_verify.short_description = "Verify selected payments"

    def bulk_reject(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f"{updated} payment(s) rejected.")
    bulk_reject.short_description = "Reject selected payments"

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'VERIFIED':
            return self.readonly_fields + ('student', 'program', 'amount', 'payment_date', 'status', 'received_by')
        return self.readonly_fields
