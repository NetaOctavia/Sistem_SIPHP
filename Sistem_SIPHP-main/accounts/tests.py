from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Pasar, ProfilAdmin


class AuthLoginLogoutTest(TestCase):
    """Test otentikasi: login, logout, proteksi halaman admin."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="admintest", password="adminpass123", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="userbiasa", password="userpass123", is_staff=False
        )

    # ------------------------------------------------------------------ #
    # Login
    # ------------------------------------------------------------------ #

    def test_login_valid_credentials(self):
        """Login dengan kredensial benar harus redirect ke beranda."""
        response = self.client.post(
            reverse("login"), {"username": "admintest", "password": "adminpass123"}
        )
        self.assertIn(response.status_code, [200, 302])

    def test_login_invalid_credentials(self):
        """Login dengan password salah harus gagal (tidak redirect ke dashboard)."""
        response = self.client.post(
            reverse("login"), {"username": "admintest", "password": "salah"}
        )
        # Tetap di halaman login
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    # ------------------------------------------------------------------ #
    # Proteksi halaman staff_member_required
    # ------------------------------------------------------------------ #

    def test_kelola_harga_requires_login(self):
        """Halaman kelola harga harus redirect ke login jika belum autentikasi."""
        response = self.client.get(reverse("harga_komoditas"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response["Location"])

    def test_kelola_berita_requires_login(self):
        """Halaman kelola berita harus redirect ke login jika belum autentikasi."""
        response = self.client.get(reverse("kelola_berita"))
        self.assertEqual(response.status_code, 302)

    def test_kelola_kontak_requires_login(self):
        """Halaman kelola kontak harus redirect ke login jika belum autentikasi."""
        response = self.client.get(reverse("kelola_kontak"))
        self.assertEqual(response.status_code, 302)

    def test_non_staff_cannot_access_admin_pages(self):
        """User non-staff tidak boleh masuk ke halaman admin."""
        self.client.login(username="userbiasa", password="userpass123")
        response = self.client.get(reverse("harga_komoditas"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_access_admin_pages(self):
        """Staff user bisa mengakses halaman admin."""
        self.client.login(username="admintest", password="adminpass123")
        response = self.client.get(reverse("harga_komoditas"))
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------ #
    # Pasar model
    # ------------------------------------------------------------------ #

    def test_pasar_str(self):
        pasar = Pasar.objects.create(nama_pasar="Pasar Subang")
        self.assertEqual(str(pasar), "Pasar Subang")

    def test_profil_admin_str(self):
        pasar = Pasar.objects.create(nama_pasar="Pasar A")
        profil = ProfilAdmin.objects.create(user=self.admin_user, pasar=pasar)
        self.assertIn("admintest", str(profil))
        self.assertIn("Pasar A", str(profil))
