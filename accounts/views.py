from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Pasar, ProfilAdmin


def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard_index")

    if request.method == "POST":
        username_req = request.POST.get("username")
        password_req = request.POST.get("password")

        user = authenticate(
            request, username=username_req, password=password_req
        )

        if user is not None:
            login(request, user)
            messages.success(
                request, f"Selamat datang kembali, {user.username}!"
            )
            return redirect("dashboard_index")
        else:
            messages.error(request, "Username atau password salah!")

    return render(request, "auth_custom/login.html")


def user_logout(request):
    logout(request)
    messages.info(request, "Anda telah berhasil keluar.")
    return redirect("beranda")


def register(request):
    if request.user.is_authenticated:
        return redirect("harga_komoditas")

    if request.method == "POST":
        username_req = request.POST.get("username")
        email_req = request.POST.get("email")
        password_req = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if password_req != password_confirm:
            messages.error(request, "Konfirmasi password tidak cocok!")
            return render(request, "auth_custom/register.html")

        if User.objects.filter(username=username_req).exists():
            messages.error(request, "Username sudah terdaftar!")
            return render(request, "auth_custom/register.html")

        user = User.objects.create_user(
            username=username_req, email=email_req, password=password_req
        )
        user.save()
        messages.success(request, "Pendaftaran berhasil! Silakan login.")
        return redirect("login")

    return render(request, "auth_custom/register.html")


@login_required(login_url='login')
def ubah_password(request):
    """Halaman ubah password untuk admin/user yang sedang login."""
    if request.method == "POST":
        password_lama = request.POST.get("password_lama")
        password_baru = request.POST.get("password_baru")
        password_konfirmasi = request.POST.get("password_konfirmasi")

        if not request.user.check_password(password_lama):
            messages.error(request, "Password lama yang Anda masukkan salah.")
            return render(request, "auth_custom/ubah_password.html")

        if len(password_baru) < 6:
            messages.error(request, "Password baru minimal 6 karakter.")
            return render(request, "auth_custom/ubah_password.html")

        if password_baru != password_konfirmasi:
            messages.error(request, "Konfirmasi password baru tidak cocok.")
            return render(request, "auth_custom/ubah_password.html")

        request.user.set_password(password_baru)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password Anda berhasil diperbarui!")
        return redirect("ubah_password")

    return render(request, "auth_custom/ubah_password.html")


@staff_member_required(login_url='login')
def kelola_users(request):
    """Halaman kelola admin & pengguna untuk Superadmin (Dinas)."""
    # Hanya Superadmin / Admin tanpa pasar yang diizinkan mengelola user
    if hasattr(request.user, 'profil_admin') and request.user.profil_admin and request.user.profil_admin.pasar:
        messages.error(request, "Akses ditolak: Hanya Admin Utama yang dapat mengelola akun admin.")
        return redirect("dashboard_index")

    if request.method == "POST" and "tambah_user" in request.POST:
        username_input = (request.POST.get("username") or "").strip()
        email_input = (request.POST.get("email") or "").strip()
        password_input = request.POST.get("password")
        role_input = request.POST.get("role")  # 'superadmin' atau 'admin_pasar'
        pasar_id_input = request.POST.get("pasar_id")

        if not username_input or not password_input:
            messages.error(request, "Username dan password wajib diisi.")
            return redirect("kelola_users")

        if User.objects.filter(username=username_input).exists():
            messages.error(request, f"Username '{username_input}' sudah digunakan.")
            return redirect("kelola_users")

        is_staff_val = True
        is_superuser_val = True if role_input == 'superadmin' else False

        user = User.objects.create_user(
            username=username_input,
            email=email_input,
            password=password_input,
            is_staff=is_staff_val,
            is_superuser=is_superuser_val
        )

        if role_input == 'admin_pasar' and pasar_id_input:
            pasar_obj = Pasar.objects.filter(id=pasar_id_input).first()
            if pasar_obj:
                ProfilAdmin.objects.create(user=user, pasar=pasar_obj)
        else:
            ProfilAdmin.objects.create(user=user, pasar=None)

        messages.success(request, f"Akun admin '{user.username}' berhasil dibuat!")
        return redirect("kelola_users")

    daftar_users = User.objects.all().select_related("profil_admin", "profil_admin__pasar").order_by("-is_superuser", "username")
    daftar_pasar = Pasar.objects.all().order_by("nama_pasar")

    context = {
        "daftar_users": daftar_users,
        "daftar_pasar": daftar_pasar,
    }
    return render(request, "auth_custom/kelola_users.html", context)


@staff_member_required(login_url='login')
def reset_password_user(request, user_id):
    """Fitur Reset Password pengguna langsung oleh Superadmin."""
    if hasattr(request.user, 'profil_admin') and request.user.profil_admin and request.user.profil_admin.pasar:
        messages.error(request, "Akses ditolak: Hanya Admin Utama yang dapat mereset password user lain.")
        return redirect("dashboard_index")

    user_target = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        password_baru = request.POST.get("password_baru")
        if not password_baru or len(password_baru) < 6:
            messages.error(request, "Password baru minimal 6 karakter.")
            return redirect("kelola_users")

        user_target.set_password(password_baru)
        user_target.save()
        messages.success(request, f"Password untuk user '{user_target.username}' berhasil direset!")
        return redirect("kelola_users")

    return redirect("kelola_users")


@staff_member_required(login_url='login')
def hapus_user(request, user_id):
    """Hapus akun admin/user."""
    if hasattr(request.user, 'profil_admin') and request.user.profil_admin and request.user.profil_admin.pasar:
        messages.error(request, "Akses ditolak: Hanya Admin Utama yang dapat menghapus user.")
        return redirect("dashboard_index")

    user_target = get_object_or_404(User, id=user_id)

    if user_target.id == request.user.id:
        messages.error(request, "Anda tidak dapat menghapus akun Anda sendiri yang sedang digunakan.")
        return redirect("kelola_users")

    username = user_target.username
    user_target.delete()
    messages.success(request, f"Akun '{username}' berhasil dihapus.")
    return redirect("kelola_users")


def lupa_password(request):
    """Halaman Lupa Password bagi petugas yang lupa kata sandi."""
    if request.method == "POST":
        username_or_email = (request.POST.get("username_or_email") or "").strip()
        user = User.objects.filter(username=username_or_email).first() or User.objects.filter(email=username_or_email).first()

        if user:
            messages.success(
                request,
                f"Permintaan reset password untuk akun '{user.username}' telah diterima. Silakan hubungi Super Admin Dinas DKUPP untuk mereset kata sandi Anda."
            )
        else:
            messages.error(request, "Username atau email tidak ditemukan dalam sistem.")

        return render(request, "auth_custom/lupa_password.html")

    return render(request, "auth_custom/lupa_password.html")
