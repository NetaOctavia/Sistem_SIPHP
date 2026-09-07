from django.contrib.auth.models import User
from django.db import models


class Pasar(models.Model):
    nama_pasar = models.CharField(max_length=100, unique=True)
    lokasi = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
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
        verbose_name_plural = "Profil Admin Pasar"

    def __str__(self):
        pasar_nama = (
            self.pasar.nama_pasar if self.pasar else "Semua Pasar (Admin Utama)"
        )
        return f"{self.user.username} - {pasar_nama}"


class Komoditas(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    satuan = models.CharField(max_length=20, default="kg")
    keterangan = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Komoditas"
        ordering = ["nama"]

    def __str__(self):
        return f"{self.nama} ({self.satuan})"


class HargaKomoditas(models.Model):
    komoditas = models.ForeignKey(
        Komoditas, on_delete=models.CASCADE, related_name="harga_set"
    )
    # Relasi utama ke model Pasar
    pasar = models.ForeignKey(
        Pasar,
        on_delete=models.CASCADE,
        related_name="harga_komoditas_set",
    )
    # Legacy field untuk migrasi data lama
    nama_pasar_lama = models.CharField(max_length=100, blank=True, null=True)

    tanggal = models.DateField()
    harga = models.DecimalField(max_digits=12, decimal_places=0)
    diinput_oleh = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Harga Komoditas"
        ordering = ["-tanggal", "pasar", "komoditas"]
        # Mencegah duplikasi: 1 komoditas hanya punya 1 entry harga per pasar per tanggal
        unique_together = ("komoditas", "pasar", "tanggal")

    def __str__(self):
        nama_p = (
            self.pasar.nama_pasar
            if self.pasar
            else (self.nama_pasar_lama or "Tanpa Pasar")
        )
        return f"{self.komoditas.nama} ({nama_p}) - {self.tanggal}: Rp {self.harga:,.0f}"


class Berita(models.Model):
    judul = models.CharField(max_length=255)
    ringkasan = models.TextField(blank=True, null=True)
    url_sumber = models.URLField(max_length=500)
    gambar_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Berita"
        ordering = ["-created_at"]

    def __str__(self):
        return self.judul


class PesanKontak(models.Model):
    nama = models.CharField(max_length=100)
    email = models.EmailField()
    telepon = models.CharField(max_length=20, blank=True, null=True)
    subjek = models.CharField(max_length=200)
    pesan = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Pesan Kontak"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nama} - {self.subjek}"