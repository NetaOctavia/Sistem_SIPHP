from django.contrib.auth.models import User
from django.db import models

# Re-export model dari app masing-masing agar backward compatible
from komoditas.models import Komoditas
from harga.models import HargaKomoditas
from berita.models import Berita
from core.models import PesanKontak


class Pasar(models.Model):
    nama_pasar = models.CharField(max_length=100, unique=True)
    lokasi = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "accounts_pasar"
        verbose_name_plural = "Pasar"
        ordering = ["nama_pasar"]

    def __str__(self):
        return self.nama_pasar


class ProfilAdmin(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profil_admin"
    )
    pasar = models.ForeignKey(
        Pasar,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Kosongkan jika user adalah Admin Utama / Superuser",
    )

    class Meta:
        db_table = "accounts_profiladmin"
        verbose_name_plural = "Profil Admin Pasar"

    def __str__(self):
        pasar_nama = (
            self.pasar.nama_pasar if self.pasar else "Semua Pasar (Admin Utama)"
        )
        return f"{self.user.username} - {pasar_nama}"