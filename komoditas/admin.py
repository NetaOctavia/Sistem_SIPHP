from django.contrib import admin
from .models import Komoditas

@admin.register(Komoditas)
class KomoditasAdmin(admin.ModelAdmin):
    list_display = ('nama_komoditas', 'kategori', 'satuan', 'created_at')
    list_filter = ('kategori',)
    search_fields = ('nama_komoditas',)