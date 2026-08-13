from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from portal import views as portal_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('portal.public_urls')),
    path('dashboard/', portal_views.dashboard_redirect, name='dashboard'),
    path('dashboard/student/', include('students.urls')),
    path('dashboard/faculty/', include('faculty.urls')),
    path('dashboard/admin/', include('portal.urls')),
    path('profile/', portal_views.profile, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
