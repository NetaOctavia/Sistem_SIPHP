from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('lupa-password/', views.lupa_password, name='lupa_password'),
    path('dashboard/password/', views.ubah_password, name='ubah_password'),
    path('dashboard/users/', views.kelola_users, name='kelola_users'),
    path('dashboard/users/reset/<int:user_id>/', views.reset_password_user, name='reset_password_user'),
    path('dashboard/users/hapus/<int:user_id>/', views.hapus_user, name='hapus_user'),
]