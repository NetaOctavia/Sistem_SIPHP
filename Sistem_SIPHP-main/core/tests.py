from django.test import Client, TestCase
from django.urls import reverse

from core.models import PesanKontak


class KontakFormTest(TestCase):
    """Test form submit kontak dan paginasi pesan kontak."""

    def setUp(self):
        from django.contrib.auth.models import User
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin_kontak", password="pass", is_staff=True
        )
        # Buat 12 pesan kontak untuk test paginasi
        for i in range(12):
            PesanKontak.objects.create(
                nama=f"Pengirim {i+1}",
                email=f"user{i+1}@example.com",
                subjek=f"Subjek {i+1}",
                pesan=f"Isi pesan {i+1}",
            )

    def test_kontak_page_accessible(self):
        """Halaman kontak publik harus bisa diakses."""
        response = self.client.get(reverse("kontak"))
        self.assertEqual(response.status_code, 200)

    def test_kirim_pesan_kontak_valid(self):
        """Form kontak valid harus menyimpan data dan redirect."""
        before = PesanKontak.objects.count()
        response = self.client.post(
            reverse("kontak"),
            {
                "nama": "Budi Santoso",
                "email": "budi@example.com",
                "telepon": "08123456789",
                "subjek": "Pertanyaan Harga",
                "pesan": "Bagaimana cara melihat harga beras terbaru?",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PesanKontak.objects.count(), before + 1)

    def test_kirim_pesan_kontak_tanpa_nama(self):
        """Form tanpa nama harus gagal validasi (tidak menyimpan data)."""
        before = PesanKontak.objects.count()
        response = self.client.post(
            reverse("kontak"),
            {
                "nama": "",  # nama kosong
                "email": "test@example.com",
                "subjek": "Test",
                "pesan": "Isi pesan.",
            },
        )
        # Tidak redirect — form error, render ulang halaman
        self.assertEqual(response.status_code, 200)
        # Data tidak tersimpan
        self.assertEqual(PesanKontak.objects.count(), before)

    def test_kirim_pesan_tanpa_email_invalid(self):
        """Form tanpa email harus gagal validasi."""
        before = PesanKontak.objects.count()
        self.client.post(
            reverse("kontak"),
            {"nama": "Tes", "email": "", "subjek": "Sub", "pesan": "Pesan."},
        )
        self.assertEqual(PesanKontak.objects.count(), before)

    def test_kelola_kontak_requires_login(self):
        """Kelola kontak harus redirect jika belum login."""
        response = self.client.get(reverse("kelola_kontak"))
        self.assertEqual(response.status_code, 302)

    def test_kelola_kontak_pagination(self):
        """Kelola kontak: halaman 1 berisi maksimal 10 item."""
        self.client.login(username="admin_kontak", password="pass")
        response = self.client.get(reverse("kelola_kontak") + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
        self.assertLessEqual(len(response.context["page_obj"].object_list), 10)

    def test_kelola_kontak_pagination_page2(self):
        """Kelola kontak halaman 2 memuat data sisa."""
        self.client.login(username="admin_kontak", password="pass")
        response = self.client.get(reverse("kelola_kontak") + "?page=2")
        self.assertEqual(response.status_code, 200)

    def test_hapus_pesan_kontak(self):
        """Staff bisa menghapus pesan kontak via POST."""
        self.client.login(username="admin_kontak", password="pass")
        pesan = PesanKontak.objects.first()
        pk = pesan.id
        response = self.client.post(reverse("hapus_kontak", args=[pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PesanKontak.objects.filter(id=pk).exists())

    def test_pesan_kontak_str(self):
        """Model PesanKontak harus menampilkan nama dan subjek."""
        pesan = PesanKontak.objects.first()
        self.assertIn("-", str(pesan))
