from django import forms
from .models import Berita


class BeritaForm(forms.ModelForm):
    class Meta:
        model = Berita
        fields = ["judul", "ringkasan", "url_sumber", "gambar_url", "gambar_file"]

    def clean_url_sumber(self):
        url = self.cleaned_data.get("url_sumber", "")
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url
