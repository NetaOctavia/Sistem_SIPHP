from django.db import models

class Komoditas(models.Model):
    nama_komoditas = models.CharField(max_length=100)
    kategori = models.CharField(max_length=50, choices=[
        ('Sembako', 'Sembako'),
        ('Bumbu', 'Bumbu Dapur'),
        ('Daging', 'Daging & Unggas'),
        ('Sayur', 'Sayur-Mayur'),
    ])
    satuan = models.CharField(max_length=20, help_text="Contoh: Kg, Liter, Ikat")
    foto = models.ImageField(upload_to='komoditas/', blank=True, null=True)
    deskripsi = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Komoditas"

    def __str__(self):
        return f"{self.nama_komoditas} ({self.satuan})"