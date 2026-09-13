from django.urls import path
from . import views

urlpatterns = [
    path('kontak/', views.kontak, name='kontak'),
    path('profil/', views.profil, name='profil'),
    path('layanan-teknis/', views.layanan_teknis, name='layanan_teknis'),
    path('dashboard/kontak/', views.kelola_kontak, name='kelola_kontak'),
    path('dashboard/kontak/hapus/<int:id>/', views.hapus_kontak, name='hapus_kontak'),
    # Alias kompatibilitas
    path('kelola-kontak/', views.kelola_kontak),
]
