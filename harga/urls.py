from django.urls import path
from . import views

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('dashboard/', views.dashboard_index, name='dashboard_index'),
    path('dashboard/harga/', views.harga_komoditas, name='harga_komoditas'),
    path('dashboard/harga/hapus-pasar/<int:pasar_id>/', views.hapus_pasar, name='hapus_pasar'),
    path('dashboard/harga/export/', views.export_harga_csv, name='export_harga_csv'),
    path('api/harga/', views.api_harga_komoditas, name='api_harga_komoditas'),
    # Alias kompatibilitas
    path('kelola-harga/', views.harga_komoditas),
]
