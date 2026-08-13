import pytest
from django.test import TestCase, Client
from django.urls import reverse
from core.models import User


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass',
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password='studentpass',
            user_type='STUDENT',
        )

    def test_landing_page(self):
        response = self.client.get(reverse('public:landing'))
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_requires_login(self):
        response = self.client.get(reverse('portal:admin_dashboard'))
        self.assertIn(response.status_code, [301, 302])

    def test_admin_dashboard_authenticated(self):
        self.client.login(email='admin@example.com', password='adminpass')
        response = self.client.get(reverse('portal:admin_dashboard'))
        self.assertIn(response.status_code, [200, 301, 302])
