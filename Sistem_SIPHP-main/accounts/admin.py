from django.contrib import admin
from .models import Pasar, ProfilAdmin


@admin.register(Pasar)
class PasarAdmin(admin.ModelAdmin):
    list_display = ("nama_pasar", "lokasi")
    search_fields = ("nama_pasar", "lokasi")


@admin.register(ProfilAdmin)
class ProfilAdminAdmin(admin.ModelAdmin):
    list_display = ("user", "pasar")
    list_filter = ("pasar",)
    search_fields = ("user__username", "pasar__nama_pasar")