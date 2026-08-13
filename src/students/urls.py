from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_dashboard, name='dashboard'),
    path('courses/', views.student_courses, name='courses'),
    path('payments/', views.student_payments, name='payments'),
]
