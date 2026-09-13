from django import forms
from .models import Komoditas


class KomoditasForm(forms.ModelForm):
    class Meta:
        model = Komoditas
        fields = ["nama", "satuan", "keterangan"]

    def clean_nama(self):
        nama = self.cleaned_data.get("nama", "").strip()
        if not nama:
            raise forms.ValidationError("Nama komoditas wajib diisi!")
        return nama

    def clean_satuan(self):
        satuan = self.cleaned_data.get("satuan", "").strip()
        return satuan or "kg"
