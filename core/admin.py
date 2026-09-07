from django.contrib import admin
from .models import PesanKontak

@admin.register(PesanKontak)
class PesanKontakAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'subjek', 'created_at', 'sudah_dibaca')
    list_filter = ('sudah_dibaca', 'created_at')
    search_fields = ('nama', 'email', 'subjek', 'pesan')
    readonly_fields = ('created_at',)