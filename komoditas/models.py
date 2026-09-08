from django.db import models


class Komoditas(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    satuan = models.CharField(max_length=20, default="kg")
    keterangan = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "accounts_komoditas"
        verbose_name_plural = "Komoditas"
        ordering = ["nama"]

    def __str__(self):
        return f"{self.nama} ({self.satuan})"