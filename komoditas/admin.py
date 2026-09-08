from django.contrib import admin
from .models import Komoditas


@admin.register(Komoditas)
class KomoditasAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "satuan", "keterangan")
    search_fields = ("nama",)