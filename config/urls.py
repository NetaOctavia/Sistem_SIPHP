from django.contrib import admin
from django.urls import path, include
from django.conf import settings               # <-- DITAMBAHKAN
from django.conf.urls.static import static     # <-- DITAMBAHKAN

urlpatterns = [
    path('admin/', admin.site.urls),          
    path('', include('accounts.urls')),       
]

if settings.DEBUG:
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])