from django.contrib import admin
from django.urls import path, include

# urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('Inicio.urls', namespace='Inicio')),
    path('admin/', include('Admin.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)