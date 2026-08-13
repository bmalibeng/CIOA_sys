from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class Program(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_months = models.IntegerField(validators=[MinValueValidator(1)])
    total_fees = models.DecimalField(max_digits=12, decimal_places=2)
    allows_installments = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Program')
        verbose_name_plural = _('Programs')
        ordering = ['name']
        indexes = [
            models.Index(fields=['code', 'is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Cohort(models.Model):
    name = models.CharField(max_length=100)
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='cohorts')
    start_date = models.DateField()
    expected_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    max_students = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Cohort')
        verbose_name_plural = _('Cohorts')
        ordering = ['-start_date']
        unique_together = ['name', 'program']
        indexes = [
            models.Index(fields=['program', 'is_active', 'start_date']),
        ]

    def __str__(self):
        return f"{self.name} ({self.program.code})"


class Student(models.Model):
    STATUS_CHOICES = (
        ('ENROLLED', 'Enrolled'),
        ('ACTIVE', 'Active'),
        ('ON_LEAVE', 'On Leave'),
        ('GRADUATED', 'Graduated'),
        ('WITHDRAWN', 'Withdrawn'),
    )

    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='students')
    cohort = models.ForeignKey(Cohort, on_delete=models.PROTECT, related_name='students')
    enrollment_date = models.DateField()
    expected_graduation_date = models.DateField()
    actual_graduation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENROLLED')
    is_active = models.BooleanField(default=True)
    excel_row_id = models.IntegerField(null=True, blank=True)
    import_batch = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')
        ordering = ['-enrollment_date']
        indexes = [
            models.Index(fields=['student_id', 'is_active']),
            models.Index(fields=['program', 'cohort', 'status']),
            models.Index(fields=['enrollment_date']),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.get_full_name()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_remaining_months(self):
        today = timezone.now().date()
        if self.expected_graduation_date <= today:
            return 0
        delta = self.expected_graduation_date - today
        return max(0, round(delta.days / 30))

    def get_progress_percentage(self):
        enrollments = self.enrollments.filter(status__in=['COMPLETED', 'FAILED', 'WITHDRAWN'])
        total = self.enrollments.count()
        if total == 0:
            return 0
        completed = enrollments.filter(status='COMPLETED').count()
        return round((completed / total) * 100, 1)

    def get_balance_due(self):
        from decimal import Decimal
        total_fees = self.program.total_fees
        verified_payments = self.payments.filter(status='VERIFIED').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        return total_fees - verified_payments

    def get_total_paid(self):
        from decimal import Decimal
        verified_payments = self.payments.filter(status='VERIFIED').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        return verified_payments


class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    programs = models.ManyToManyField(Program, related_name='courses')
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['course_code']
        indexes = [
            models.Index(fields=['course_code', 'is_active']),
        ]

    def __str__(self):
        return f"{self.course_code} - {self.title}"


class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('ENROLLED', 'Enrolled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('WITHDRAWN', 'Withdrawn'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    letter_grade = models.CharField(max_length=5, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENROLLED')
    excel_row_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'course', 'status']),
            models.Index(fields=['enrollment_date']),
        ]

    def __str__(self):
        return f"{self.student} - {self.course}"


class Payment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    received_by = models.ForeignKey('core.User', on_delete=models.PROTECT, related_name='payments_received')
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    excel_row_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['student', 'status', 'payment_date']),
            models.Index(fields=['receipt_number']),
        ]

    def __str__(self):
        return f"{self.receipt_number} - M {self.amount:,.2f}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)

    def generate_receipt_number(self):
        from django.db.models import Max
        year = timezone.now().year
        last = Payment.objects.filter(
            receipt_number__startswith=f"CASH-{year}-"
        ).aggregate(Max('receipt_number'))['receipt_number__max']
        if last:
            try:
                num = int(last.split('-')[-1]) + 1
            except (IndexError, ValueError):
                num = 1
        else:
            num = 1
        return f"CASH-{year}-{num:04d}"


class ContinuousImportLog(models.Model):
    import_name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)
    stats = models.JSONField(default=dict)
    imported_at = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey('core.User', on_delete=models.PROTECT, related_name='import_logs')
    dry_run = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Continuous Import Log')
        verbose_name_plural = _('Continuous Import Logs')
        ordering = ['-imported_at']

    def __str__(self):
        return f"{self.import_name} - {self.imported_at}"
