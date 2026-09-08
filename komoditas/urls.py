from django.urls import path
from . import views

urlpatterns = [
    path('komoditas/', views.komoditas, name='komoditas'),
    path('dashboard/komoditas/', views.komoditas, name='kelola_komoditas'),
    path('dashboard/komoditas/edit/<int:id>/', views.edit_komoditas, name='edit_komoditas'),
    path('dashboard/komoditas/hapus/<int:id>/', views.hapus_komoditas, name='hapus_komoditas'),
    path('api/komoditas/', views.api_daftar_komoditas, name='api_daftar_komoditas'),
]
