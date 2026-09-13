from django.contrib.auth.models import User
from django.db import models


class HargaKomoditas(models.Model):
    komoditas = models.ForeignKey(
        "komoditas.Komoditas", on_delete=models.CASCADE, related_name="harga_set"
    )
    pasar = models.ForeignKey(
        "accounts.Pasar",
        on_delete=models.CASCADE,
        related_name="harga_komoditas_set",
    )
    tanggal = models.DateField()
    harga = models.DecimalField(max_digits=12, decimal_places=0)
    diinput_oleh = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "accounts_hargakomoditas"
        verbose_name_plural = "Harga Komoditas"
        ordering = ["-tanggal", "pasar", "komoditas"]
        unique_together = ("komoditas", "pasar", "tanggal")

    def __str__(self):
        nama_p = self.pasar.nama_pasar if self.pasar else "Tanpa Pasar"
        return f"{self.komoditas.nama} ({nama_p}) - {self.tanggal}: Rp {self.harga:,.0f}"