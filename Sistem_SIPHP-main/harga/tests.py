from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Pasar
from harga.models import HargaKomoditas
from komoditas.models import Komoditas


class HargaKomoditasModelTest(TestCase):
    """Test model HargaKomoditas dan kalkulasi dasar."""

    def setUp(self):
        self.pasar = Pasar.objects.create(nama_pasar="Pasar Uji")
        self.komoditas = Komoditas.objects.create(nama="Beras", satuan="kg")
        self.admin = User.objects.create_user(
            username="petugas", password="pass", is_staff=True
        )
        self.today = timezone.now().date()

    def test_create_harga(self):
        """Harga berhasil dibuat dan nilai terbaca dengan benar."""
        harga = HargaKomoditas.objects.create(
            komoditas=self.komoditas,
            pasar=self.pasar,
            tanggal=self.today,
            harga=15000,
            diinput_oleh=self.admin,
        )
        self.assertEqual(int(harga.harga), 15000)
        self.assertIn("Beras", str(harga))

    def test_unique_together_constraint(self):
        """Tidak boleh ada dua harga untuk kombinasi komoditas+pasar+tanggal yang sama."""
        from django.db import IntegrityError

        HargaKomoditas.objects.create(
            komoditas=self.komoditas,
            pasar=self.pasar,
            tanggal=self.today,
            harga=15000,
        )
        with self.assertRaises(IntegrityError):
            HargaKomoditas.objects.create(
                komoditas=self.komoditas,
                pasar=self.pasar,
                tanggal=self.today,
                harga=16000,
            )

    # ------------------------------------------------------------------ #
    # View: Export CSV
    # ------------------------------------------------------------------ #

    def test_export_csv_requires_login(self):
        """Export CSV harus membutuhkan login staff."""
        client = Client()
        response = client.get(reverse("export_harga_csv"))
        self.assertEqual(response.status_code, 302)

    def test_export_csv_returns_csv_file(self):
        """Staff yang login bisa mendownload file CSV."""
        HargaKomoditas.objects.create(
            komoditas=self.komoditas,
            pasar=self.pasar,
            tanggal=self.today,
            harga=15000,
            diinput_oleh=self.admin,
        )
        client = Client()
        client.login(username="petugas", password="pass")
        response = client.get(reverse("export_harga_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("rekap_harga_pangan", response["Content-Disposition"])

    def test_export_csv_filter_by_pasar(self):
        """CSV export dengan filter pasar_id hanya berisi data pasar tersebut."""
        pasar2 = Pasar.objects.create(nama_pasar="Pasar Lain")
        HargaKomoditas.objects.create(
            komoditas=self.komoditas, pasar=self.pasar, tanggal=self.today, harga=15000
        )
        HargaKomoditas.objects.create(
            komoditas=self.komoditas, pasar=pasar2, tanggal=self.today, harga=18000
        )
        client = Client()
        client.login(username="petugas", password="pass")
        response = client.get(
            reverse("export_harga_csv") + f"?pasar_id={self.pasar.id}"
        )
        content = response.content.decode("utf-8-sig")
        self.assertIn("Pasar Uji", content)
        self.assertNotIn("Pasar Lain", content)

    # ------------------------------------------------------------------ #
    # View: API Harga
    # ------------------------------------------------------------------ #

    def test_api_harga_returns_json(self):
        """Endpoint API harga harus mengembalikan JSON valid."""
        import json

        HargaKomoditas.objects.create(
            komoditas=self.komoditas, pasar=self.pasar, tanggal=self.today, harga=15000
        )
        client = Client()
        response = client.get(reverse("api_harga_komoditas"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["count"], 1)
        self.assertIn("komoditas", data["data"][0])

    # ------------------------------------------------------------------ #
    # View: Batch Input Harga
    # ------------------------------------------------------------------ #

    def test_batch_input_harga(self):
        """Staff bisa menginput harga batch via POST."""
        client = Client()
        client.login(username="petugas", password="pass")
        response = client.post(
            reverse("harga_komoditas"),
            {
                "pasar_id": self.pasar.id,
                "tanggal": str(self.today),
                f"harga_{self.komoditas.id}": "15000",
            },
        )
        # Harus redirect setelah sukses
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            HargaKomoditas.objects.filter(
                komoditas=self.komoditas, pasar=self.pasar, tanggal=self.today
            ).exists()
        )
