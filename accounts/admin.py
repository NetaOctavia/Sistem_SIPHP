from django.contrib import admin
from .models import Komoditas, HargaKomoditas

@admin.register(Komoditas)
class KomoditasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama', 'satuan', 'keterangan')
    search_fields = ('nama',)

@admin.register(HargaKomoditas)
class HargaKomoditasAdmin(admin.ModelAdmin):
    list_display = ('komoditas', 'get_satuan', 'tanggal', 'harga')
    list_filter = ('komoditas', 'tanggal')
    search_fields = ('komoditas__nama',)

    @admin.display(description='Satuan')
    def get_satuan(self, obj):
        return obj.komoditas.satuan 