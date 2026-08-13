import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from core.models import User
from students.models import Program, Cohort, Student, Course, Enrollment, Payment


class StudentModelTests(TestCase):
    def setUp(self):
        self.program = Program.objects.create(
            code='FAS001',
            name='Fashion Design',
            duration_months=12,
            total_fees=Decimal('150000.00'),
            allows_installments=True,
        )
        self.cohort = Cohort.objects.create(
            name='2024-01',
            program=self.program,
            start_date=date(2024, 1, 1),
            expected_end_date=date(2025, 1, 1),
            max_students=30,
        )
        self.student = Student.objects.create(
            student_id='STU001',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            program=self.program,
            cohort=self.cohort,
            enrollment_date=date(2024, 1, 1),
            expected_graduation_date=date(2025, 1, 1),
        )

    def test_student_remaining_months(self):
        today = date.today()
        self.student.expected_graduation_date = today + timedelta(days=60)
        self.assertEqual(self.student.get_remaining_months(), 2)

    def test_student_progress_percentage(self):
        course1 = Course.objects.create(course_code='CRS001', title='Course 1', credits=3)
        Enrollment.objects.create(student=self.student, course=course1, status='COMPLETED', enrollment_date=date(2024, 1, 1))
        course2 = Course.objects.create(course_code='CRS002', title='Course 2', credits=3)
        Enrollment.objects.create(student=self.student, course=course2, status='ENROLLED', enrollment_date=date(2024, 1, 1))
        self.assertEqual(self.student.get_progress_percentage(), 50.0)

    def test_student_balance_due(self):
        Payment.objects.create(
            student=self.student,
            program=self.program,
            amount=Decimal('50000.00'),
            payment_date=date.today(),
            received_by=User.objects.create_user(email='admin@example.com', password='test', user_type='ADMIN'),
            status='VERIFIED',
        )
        self.assertEqual(self.student.get_balance_due(), Decimal('100000.00'))

    def test_student_total_paid(self):
        Payment.objects.create(
            student=self.student,
            program=self.program,
            amount=Decimal('75000.00'),
            payment_date=date.today(),
            received_by=User.objects.create_user(email='admin@example.com', password='test', user_type='ADMIN'),
            status='VERIFIED',
        )
        self.assertEqual(self.student.get_total_paid(), Decimal('75000.00'))


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='student@example.com',
            password='testpass123',
            user_type='STUDENT',
        )

    def test_login(self):
        response = self.client.post(reverse('login'), {'username': 'student@example.com', 'password': 'testpass123'})
        self.assertIn(response.status_code, [301, 302])

    def test_redirect_authenticated(self):
        self.client.login(email='student@example.com', password='testpass123')
        response = self.client.get(reverse('public:landing'))
        self.assertEqual(response.status_code, 200)
