from django.db import models
from django.contrib.auth.models import User

class Berita(models.Model):
    judul = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    penulis = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    gambar = models.ImageField(upload_to='berita/')
    konten = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Berita"

    def __str__(self):
        return self.judul