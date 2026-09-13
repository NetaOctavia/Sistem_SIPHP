from django.test import Client, TestCase
from django.urls import reverse

from berita.models import Berita


class BeritaModelTest(TestCase):
    """Test model Berita."""

    def test_create_berita_with_url(self):
        b = Berita.objects.create(
            judul="Harga Beras Naik",
            ringkasan="Ringkasan singkat.",
            url_sumber="https://example.com",
        )
        self.assertEqual(str(b), "Harga Beras Naik")

    def test_display_gambar_returns_url(self):
        """display_gambar harus mengembalikan gambar_url jika tidak ada file."""
        b = Berita.objects.create(
            judul="Berita Tes",
            gambar_url="https://example.com/img.jpg",
        )
        self.assertEqual(b.display_gambar, "https://example.com/img.jpg")

    def test_display_gambar_empty_if_no_image(self):
        """display_gambar mengembalikan string kosong jika tidak ada gambar."""
        b = Berita.objects.create(judul="Berita Tanpa Gambar")
        self.assertEqual(b.display_gambar, "")


class BeritaViewTest(TestCase):
    """Test CRUD berita via HTTP."""

    def setUp(self):
        from django.contrib.auth.models import User
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin_berita", password="pass", is_staff=True
        )
        # Buat beberapa berita untuk test paginasi
        for i in range(12):
            Berita.objects.create(judul=f"Berita {i+1}", ringkasan=f"Isi {i+1}")

    def test_berita_publik_accessible(self):
        """Halaman berita publik harus bisa diakses tanpa login."""
        response = self.client.get(reverse("berita"))
        self.assertEqual(response.status_code, 200)

    def test_kelola_berita_requires_login(self):
        """Kelola berita harus redirect jika belum login."""
        response = self.client.get(reverse("kelola_berita"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_access_kelola_berita(self):
        """Staff bisa mengakses halaman kelola berita."""
        self.client.login(username="admin_berita", password="pass")
        response = self.client.get(reverse("kelola_berita"))
        self.assertEqual(response.status_code, 200)

    def test_kelola_berita_pagination(self):
        """Kelola berita: halaman 1 berisi page_obj dengan paginator."""
        self.client.login(username="admin_berita", password="pass")
        response = self.client.get(reverse("kelola_berita") + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
        self.assertLessEqual(len(response.context["page_obj"].object_list), 10)

    def test_tambah_berita_via_post(self):
        """Staff bisa menambah berita via POST."""
        self.client.login(username="admin_berita", password="pass")
        before_count = Berita.objects.count()
        response = self.client.post(
            reverse("kelola_berita"),
            {
                "judul": "Berita Baru Test",
                "ringkasan": "Isi berita baru.",
                "url_sumber": "https://example.com/berita-baru",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Berita.objects.count(), before_count + 1)

    def test_hapus_berita(self):
        """Staff bisa menghapus berita via POST."""
        self.client.login(username="admin_berita", password="pass")
        b = Berita.objects.create(judul="Hapus Ini", ringkasan="test")
        pk = b.id
        response = self.client.post(reverse("hapus_berita", args=[pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Berita.objects.filter(id=pk).exists())

    def test_api_berita_returns_json(self):
        """API berita mengembalikan JSON valid dengan field yang benar."""
        import json
        response = self.client.get(reverse("api_daftar_berita"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        if data["count"] > 0:
            self.assertIn("judul", data["data"][0])
            self.assertIn("gambar", data["data"][0])
