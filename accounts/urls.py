from django.urls import path
from . import views

urlpatterns = [
    # Public Routes
    path('', views.beranda, name='beranda'),
    path('berita/', views.berita, name='berita'),
    path('komoditas/', views.komoditas, name='komoditas'),
    path('kontak/', views.kontak, name='kontak'),
    path('profil/', views.profil, name='profil'),
    path('layanan-teknis/', views.layanan_teknis, name='layanan_teknis'),

    # Auth Routes
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    # Admin - Kelola Harga & Komoditas
    path('kelola-harga/', views.harga_komoditas, name='harga_komoditas'),
    path('kelola-harga/edit/<int:id>/', views.edit_komoditas, name='edit_komoditas'),
    path('kelola-harga/hapus/<int:id>/', views.hapus_komoditas, name='hapus_komoditas'),
    path('kelola-harga/hapus-pasar/<int:pasar_id>/', views.hapus_pasar, name='hapus_pasar'),

    # Admin - Kelola Berita
    path('kelola-berita/', views.kelola_berita, name='kelola_berita'),
    path('edit-berita/<int:id>/', views.edit_berita, name='edit_berita'),
    path('kelola-berita/hapus/<int:id>/', views.hapus_berita, name='hapus_berita'),

    # Admin - Kelola Pesan Kontak
    path('kelola-kontak/', views.kelola_kontak, name='kelola_kontak'),
    path('kelola-kontak/hapus/<int:id>/', views.hapus_kontak, name='hapus_kontak'),

    
]