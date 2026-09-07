from django.db import models
from komoditas.models import Komoditas

class HargaHarian(models.Model):
    komoditas = models.ForeignKey(Komoditas, on_delete=models.CASCADE, related_name='daftar_harga')
    wilayah = models.CharField(max_length=100, help_text="Nama Kabupaten/Kecamatan/Pasar")
    latitude = models.FloatField(help_text="Koordinat Latitude untuk Peta Leaflet.js")
    longitude = models.FloatField(help_text="Koordinat Longitude untuk Peta Leaflet.js")
    harga = models.DecimalField(max_digits=12, decimal_places=2)
    tanggal = models.DateField()

    class Meta:
        verbose_name_plural = "Harga Harian"
        ordering = ['-tanggal']

    def __str__(self):
        return f"{self.komoditas.nama_komoditas} - {self.wilayah} (Rp {self.harga:,.0f})"