from django import forms
from django.contrib.auth.models import User
from .models import Komoditas, HargaKomoditas

INPUT_STYLE = 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none'


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_STYLE,
            'placeholder': 'Masukkan password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_STYLE,
            'placeholder': 'Konfirmasi password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Masukkan username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Nama depan'
            }),
            'last_name': forms.TextInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Nama belakang'
            }),
            'email': forms.EmailInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'nama@email.com'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password dan Konfirmasi Password tidak cocok!")
        return cleaned_data


class KomoditasForm(forms.ModelForm):
    class Meta:
        model = Komoditas
        fields = ['nama', 'satuan', 'keterangan']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Nama Komoditas (misal: Beras Premium)'
            }),
            'satuan': forms.TextInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Satuan (misal: Kg, Liter)'
            }),
            'keterangan': forms.Textarea(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Keterangan tambahan...',
                'rows': 3
            }),
        }


class HargaKomoditasForm(forms.ModelForm):
    class Meta:
        model = HargaKomoditas
        fields = ['komoditas', 'tanggal', 'harga']
        widgets = {
            'komoditas': forms.Select(attrs={
                'class': INPUT_STYLE
            }),
            'tanggal': forms.DateInput(attrs={
                'type': 'date',
                'class': INPUT_STYLE
            }),
            'harga': forms.NumberInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Masukkan harga (Rp)'
            }),
        } 