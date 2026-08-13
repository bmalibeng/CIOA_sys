from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import User


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Faculty')
        verbose_name_plural = _('Faculty')
        indexes = [
            models.Index(fields=['faculty_id', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.faculty_id})"

    def get_full_name(self):
        return self.user.get_full_name()

    def get_pending_grades_count(self):
        return self.courses.filter(
            enrollments__status='IN_PROGRESS',
            is_active=True
        ).count()
