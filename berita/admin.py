from django.contrib import admin
from .models import Berita

@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    list_display = ('judul', 'penulis', 'created_at')
    list_filter = ('created_at', 'penulis')
    search_fields = ('judul', 'konten')
    prepopulated_fields = {'slug': ('judul',)}