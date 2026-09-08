from django import forms
from django.contrib.auth.models import User

# Re-export dari app masing-masing
from komoditas.forms import KomoditasForm


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Masukkan password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Konfirmasi password"}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Masukkan username"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Nama depan"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Nama belakang"}),
            "email": forms.EmailInput(attrs={"placeholder": "nama@email.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Gunakan class semantik modular, bukan class Tailwind hardcode
            field.widget.attrs.setdefault("class", "form-input")
            # Tambah autocomplete off untuk password field
            if "password" in field_name:
                field.widget.attrs.setdefault("autocomplete", "new-password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password dan Konfirmasi Password tidak cocok!")
        return cleaned_data