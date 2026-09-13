from django.contrib import admin
from .models import Berita


@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    list_display = ("judul", "created_at", "updated_at")
    search_fields = ("judul", "ringkasan")