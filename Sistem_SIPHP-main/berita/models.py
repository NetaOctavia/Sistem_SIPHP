from django.db import models


class Berita(models.Model):
    judul = models.CharField(max_length=255)
    ringkasan = models.TextField(blank=True, null=True)
    url_sumber = models.URLField(max_length=500, blank=True, null=True)
    gambar_url = models.URLField(max_length=500, blank=True, null=True)
    gambar_file = models.ImageField(upload_to="berita/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_berita"
        verbose_name_plural = "Berita"
        ordering = ["-created_at"]

    def __str__(self):
        return self.judul

    @property
    def display_gambar(self):
        if self.gambar_file:
            return self.gambar_file.url
        return self.gambar_url or ""