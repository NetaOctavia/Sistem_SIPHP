from django.contrib import admin
from .models import HargaHarian

@admin.register(HargaHarian)
class HargaHarianAdmin(admin.ModelAdmin):
    list_display = ('komoditas', 'wilayah', 'harga', 'tanggal')
    list_filter = ('tanggal', 'wilayah', 'komoditas')
    search_fields = ('wilayah', 'komoditas__nama_komoditas')
    date_hierarchy = 'tanggal'