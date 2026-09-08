from django.urls import path
from . import views

urlpatterns = [
    path('berita/', views.berita, name='berita'),
    path('kelola-berita/', views.kelola_berita, name='kelola_berita'),
    path('edit-berita/<int:id>/', views.edit_berita, name='edit_berita'),
    path('kelola-berita/hapus/<int:id>/', views.hapus_berita, name='hapus_berita'),
    path('api/berita/', views.api_daftar_berita, name='api_daftar_berita'),
]
