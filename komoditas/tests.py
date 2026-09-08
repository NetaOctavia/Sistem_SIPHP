from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Pasar
from harga.models import HargaKomoditas
from komoditas.models import Komoditas


class KomoditasModelTest(TestCase):
    """Test model Komoditas."""

    def test_create_komoditas(self):
        kom = Komoditas.objects.create(nama="Jagung", satuan="kg")
        self.assertEqual(str(kom), "Jagung (kg)")  # __str__ = f"{nama} ({satuan})"
        self.assertEqual(kom.satuan, "kg")

    def test_komoditas_str(self):
        kom = Komoditas.objects.create(nama="Gula Pasir", satuan="kg")
        self.assertIn("Gula Pasir", str(kom))


class KomoditasPaginationTest(TestCase):
    """Test paginasi tabel komoditas (10 item/halaman)."""

    def setUp(self):
        # Buat 15 komoditas untuk test paginasi
        self.komoditas_list = []
        for i in range(15):
            k = Komoditas.objects.create(nama=f"Komoditas {i+1:02d}", satuan="kg")
            self.komoditas_list.append(k)

    def test_pagination_10_items_per_page(self):
        """Halaman 1 harus memiliki maksimal 10 item."""
        paginator = Paginator(
            Komoditas.objects.all().order_by("nama"), 10
        )
        page1 = paginator.get_page(1)
        self.assertEqual(len(page1.object_list), 10)

    def test_pagination_page_2_has_remaining(self):
        """Halaman 2 harus memiliki 5 item sisa."""
        paginator = Paginator(
            Komoditas.objects.all().order_by("nama"), 10
        )
        page2 = paginator.get_page(2)
        self.assertEqual(len(page2.object_list), 5)

    def test_komoditas_view_pagination_page1(self):
        """View komoditas publik mengembalikan HTTP 200 dengan halaman 1."""
        client = Client()
        response = client.get(reverse("komoditas") + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)

    def test_komoditas_view_pagination_page2(self):
        """View komoditas halaman 2 mengembalikan HTTP 200."""
        client = Client()
        response = client.get(reverse("komoditas") + "?page=2")
        self.assertEqual(response.status_code, 200)


class KomoditasTrenTest(TestCase):
    """Test agregasi harga 7 hari terakhir."""

    def setUp(self):
        self.pasar = Pasar.objects.create(nama_pasar="Pasar Uji")
        self.komoditas = Komoditas.objects.create(nama="Beras Uji", satuan="kg")
        self.admin = User.objects.create_user(
            username="petugastest", password="pass", is_staff=True
        )
        today = timezone.now().date()
        # Masukkan data 3 hari terakhir
        for i in range(3):
            from datetime import timedelta
            HargaKomoditas.objects.create(
                komoditas=self.komoditas,
                pasar=self.pasar,
                tanggal=today - timedelta(days=i),
                harga=10000 + (i * 500),
            )

    def test_harga_tersedia_untuk_komoditas(self):
        """Data harga tersedia di database untuk komoditas uji."""
        from harga.models import HargaKomoditas
        count = HargaKomoditas.objects.filter(komoditas=self.komoditas).count()
        self.assertEqual(count, 3)

    def test_api_komoditas_returns_json(self):
        """API daftar komoditas mengembalikan JSON valid."""
        import json
        client = Client()
        response = client.get(reverse("api_daftar_komoditas"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        names = [d["nama"] for d in data["data"]]
        self.assertIn("Beras Uji", names)
