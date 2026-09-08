from django import forms
from .models import PesanKontak


class PesanKontakForm(forms.ModelForm):
    class Meta:
        model = PesanKontak
        fields = ["nama", "email", "telepon", "subjek", "pesan"]

    def clean_nama(self):
        nama = self.cleaned_data.get("nama", "").strip()
        if not nama:
            raise forms.ValidationError("Nama wajib diisi!")
        return nama

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise forms.ValidationError("Email wajib diisi!")
        return email

    def clean_pesan(self):
        pesan = self.cleaned_data.get("pesan", "").strip()
        if not pesan:
            raise forms.ValidationError("Pesan tidak boleh kosong!")
        return pesan
