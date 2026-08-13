from django.urls import path
from portal import views as portal_views
from students import views as student_views

app_name = 'public'

urlpatterns = [
    path('', portal_views.landing_page, name='landing'),
    path('courses/', student_views.student_courses, name='courses'),
    path('courses/<int:pk>/', portal_views.course_detail, name='course_detail'),
    path('profile/', portal_views.profile, name='profile'),
]
