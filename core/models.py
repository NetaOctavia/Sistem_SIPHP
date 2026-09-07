from django.db import models

class PesanKontak(models.Model):
    nama = models.CharField(max_length=100)
    email = models.EmailField()
    subjek = models.CharField(max_length=150)
    pesan = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sudah_dibaca = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Pesan Kontak"

    def __str__(self):
        return f"Pesan dari {self.nama} - {self.subjek}"