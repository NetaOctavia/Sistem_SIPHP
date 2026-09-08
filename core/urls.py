from django.urls import path
from . import views

urlpatterns = [
    path('kontak/', views.kontak, name='kontak'),
    path('profil/', views.profil, name='profil'),
    path('layanan-teknis/', views.layanan_teknis, name='layanan_teknis'),
    path('kelola-kontak/', views.kelola_kontak, name='kelola_kontak'),
    path('kelola-kontak/hapus/<int:id>/', views.hapus_kontak, name='hapus_kontak'),
]
