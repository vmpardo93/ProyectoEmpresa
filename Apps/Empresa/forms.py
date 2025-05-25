from django import forms
from .models import Organization, UserProfile
from django.contrib.auth.models import User

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'type', 'website', 'phone', 'nit', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la organización'}),
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de organización'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.ejemplo.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIT'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'})
        }
        labels = {
            'name': 'Nombre',
            'type': 'Tipo',
            'website': 'Sitio Web',
            'phone': 'Teléfono',
            'nit': 'NIT',
            'logo': 'Logo'
        }

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        label='Apellido'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
        label='Correo Electrónico'
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='Foto de Perfil'
    )

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Actualizar también el modelo User
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile 