from django.db import models


class PesanKontak(models.Model):
    nama = models.CharField(max_length=100)
    email = models.EmailField()
    telepon = models.CharField(max_length=20, blank=True, null=True)
    subjek = models.CharField(max_length=200)
    pesan = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_pesankontak"
        verbose_name_plural = "Pesan Kontak"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nama} - {self.subjek}"