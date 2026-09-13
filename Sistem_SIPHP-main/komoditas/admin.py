from django.contrib import admin
from .models import Komoditas


@admin.register(Komoditas)
class KomoditasAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "kategori", "satuan", "keterangan")
    list_filter = ("kategori",)
    search_fields = ("nama", "kategori")