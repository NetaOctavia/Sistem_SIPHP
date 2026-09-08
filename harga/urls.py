from django.urls import path
from . import views

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('kelola-harga/', views.harga_komoditas, name='harga_komoditas'),
    path('kelola-harga/hapus-pasar/<int:pasar_id>/', views.hapus_pasar, name='hapus_pasar'),
    path('kelola-harga/export/', views.export_harga_csv, name='export_harga_csv'),
    path('api/harga/', views.api_harga_komoditas, name='api_harga_komoditas'),
]
