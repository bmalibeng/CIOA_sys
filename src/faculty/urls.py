from django.urls import path
from . import views

app_name = 'faculty'

urlpatterns = [
    path('', views.faculty_dashboard, name='dashboard'),
    path('courses/', views.faculty_courses, name='courses'),
    path('grades/', views.faculty_grades, name='grades'),
]
