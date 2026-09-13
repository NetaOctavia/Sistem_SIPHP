from django.contrib import admin
from .models import PesanKontak


@admin.register(PesanKontak)
class PesanKontakAdmin(admin.ModelAdmin):
    list_display = ("nama", "email", "telepon", "subjek", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("nama", "email", "subjek", "pesan")