from django.contrib import admin
from .models import HargaKomoditas


@admin.register(HargaKomoditas)
class HargaKomoditasAdmin(admin.ModelAdmin):
    list_display = ("komoditas", "pasar", "get_satuan", "tanggal", "harga")
    list_filter = ("pasar", "komoditas", "tanggal")
    search_fields = ("komoditas__nama", "pasar__nama_pasar")

    @admin.display(description="Satuan")
    def get_satuan(self, obj):
        return obj.komoditas.satuan