from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.html import format_html
from django.contrib.auth.forms import UserCreationForm
from .models import Organization, UserProfile, Category
from django.contrib.auth.models import User

class CustomCheckboxSelectMultiple(CheckboxSelectMultiple):
    """Widget personalizado para mostrar checkboxes en una grid responsiva de Bootstrap"""
    
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        
        # Convertir value a lista de strings para comparación
        if isinstance(value, (list, tuple)):
            str_values = [str(v) for v in value]
        else:
            str_values = [str(value)] if value else []
        
        output = ['<div class="container-fluid p-0"><div class="row g-2">']
        
        for option_value, option_label in self.choices:
            checked = str(option_value) in str_values
            checkbox_id = f"{name}_{option_value}"
            
            output.append(
                f'<div class="col-sm-6 col-md-4">'
                f'  <div class="form-check border rounded p-2 h-100" '
                f'       style="transition: all 0.2s; cursor: pointer;" '
                f'       onmouseover="this.style.borderColor=\'#007bff\'; this.style.backgroundColor=\'#f8f9fa\';" '
                f'       onmouseout="this.style.borderColor=\'#dee2e6\'; this.style.backgroundColor=\'transparent\';">'
                f'    <input type="checkbox" class="form-check-input" '
                f'           id="{checkbox_id}" name="{name}" value="{option_value}"'
                f'           {"checked" if checked else ""}>'
                f'    <label class="form-check-label w-100 d-flex align-items-center" for="{checkbox_id}">'
                f'      <span class="ms-1">{option_label}</span>'
                f'    </label>'
                f'  </div>'
                f'</div>'
            )
        
        output.append('</div></div>')
        return format_html(''.join(output))

class SimpleCheckboxSelectMultiple(CheckboxSelectMultiple):
    """Widget simple alternativo para checkboxes con mejor estructura"""
    
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        
        # Convertir value a lista de strings para comparación
        if isinstance(value, (list, tuple)):
            str_values = [str(v) for v in value]
        else:
            str_values = [str(value)] if value else []
        
        output = ['<div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0;">']
        
        for option_value, option_label in self.choices:
            checked = str(option_value) in str_values
            checkbox_id = f"{name}_{option_value}"
            
            output.append(
                f'<div class="form-check" style="flex: 0 0 calc(50% - 5px); min-width: 200px;">'
                f'  <input type="checkbox" class="form-check-input" '
                f'         id="{checkbox_id}" name="{name}" value="{option_value}"'
                f'         {"checked" if checked else ""}>'
                f'  <label class="form-check-label" for="{checkbox_id}">'
                f'    {option_label}'
                f'  </label>'
                f'</div>'
            )
        
        output.append('</div>')
        return format_html(''.join(output))

class OrganizationForm(forms.ModelForm):
    # Opciones de widget para categorías:
    # SimpleCheckboxSelectMultiple() - Widget simple con flexbox (funcional, sin problemas de superposición)
    # CustomCheckboxSelectMultiple() - Widget avanzado con Bootstrap grid (más elegante)
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(status=True),
        widget=SimpleCheckboxSelectMultiple(),
        required=False,
        label='Categorías',
        help_text='Selecciona las categorías que aplican a tu organización'
    )
    
    class Meta:
        model = Organization
        fields = ['name', 'type', 'website', 'phone', 'nit', 'logo', 'services', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la organización'}),
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de organización'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.ejemplo.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIT'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'services': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Consultoría, Desarrollo Web, Marketing Digital',
                'data-role': 'tagsinput'  # Para usar Bootstrap Tags Input
            })
        }
        labels = {
            'name': 'Nombre',
            'type': 'Tipo',
            'website': 'Sitio Web',
            'phone': 'Teléfono',
            'nit': 'NIT',
            'logo': 'Logo',
            'services': 'Servicios'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que siempre se muestren solo categorías activas
        self.fields['categories'].queryset = Category.objects.filter(status=True).order_by('name')
        
        # Si estamos editando una organización existente, preseleccionar sus categorías
        if self.instance and self.instance.pk:
            self.fields['categories'].initial = self.instance.categories.filter(status=True)
    
    def save(self, commit=True):
        organization = super().save(commit=False)
        if commit:
            organization.save()
            # Guardar las categorías seleccionadas
            self.save_m2m()
        return organization

class UserProfileForm(forms.ModelForm):
    # Campos del modelo User (para evitar duplicación)
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        label='Apellido'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
        label='Correo Electrónico'
    )

    # Campos específicos del UserProfile (sin duplicación)
    class Meta:
        model = UserProfile
        fields = ['image', 'bio', 'phone', 'location']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Cuéntanos sobre ti...',
                'rows': 4
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+57 300 123 4567'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ciudad, País'
            }),
            #'language': forms.Select(attrs={'class': 'form-control'}),
            #'receive_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'image': 'Foto de Perfil',
            'bio': 'Biografía',
            'phone': 'Teléfono',
            'location': 'Ubicación',
            #'language': 'Idioma',
            #'receive_notifications': 'Recibir Notificaciones',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar campos del User si existe la instancia
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Establecer el idioma por defecto a español
        profile.language = 'es-es'
        
        # Actualizar campos del modelo User (sin duplicación)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            profile.save()
        return profile

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría',
                'maxlength': '100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la categoría (opcional)',
                'rows': 4
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'status': 'Activa'
        }
        help_texts = {
            'name': 'Ingresa un nombre único para la categoría',
            'description': 'Proporciona una descripción detallada (opcional)',
            'status': 'Marca si la categoría está activa y disponible para usar'
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Verificar que el nombre sea único (case insensitive)
            existing = Category.objects.filter(name__iexact=name)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('Ya existe una categoría con este nombre.')
        return name

class SignupForm(UserCreationForm):
    """
    Formulario de registro personalizado que crea User + UserProfile
    """
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        }),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        }),
        label='Apellido'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        }),
        label='Correo Electrónico'
    )
    bio = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Cuéntanos un poco sobre ti (opcional)',
            'rows': 3
        }),
        label='Biografía (Opcional)'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+57 300 123 4567'
        }),
        label='Teléfono (Opcional)'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario único'
            }),
        }
        labels = {
            'username': 'Nombre de Usuario',
        }
        help_texts = {
            'username': 'Letras, dígitos y @/./+/-/_ únicamente.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets de campos heredados
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })
        
        # Personalizar labels
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return email

    def save(self, commit=True, request=None):
        # Crear el usuario como INACTIVO
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  # Usuario inactivo hasta que admin lo active
        
        if commit:
            user.save()
            
            # Detectar location automáticamente
            location = self.detect_location(request)
            
            # Crear UserProfile automáticamente
            profile = UserProfile.objects.create(
                user=user,
                bio=self.cleaned_data.get('bio', ''),
                phone=self.cleaned_data.get('phone', ''),
                location=location,
                language='es-es',  # Español por defecto
                receive_notifications=True
            )
        
        return user
    
    def detect_location(self, request):
        """
        Detecta la ubicación del usuario automáticamente
        """
        if not request:
            return 'No especificada'
            
        # Intentar obtener IP del usuario
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Por ahora, location simple basada en headers del navegador
        # En producción podrías usar APIs como GeoIP, MaxMind, etc.
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Detección básica por idioma del navegador
        if 'es' in accept_language.lower():
            if 'co' in accept_language.lower():
                return 'Colombia'
            elif 'mx' in accept_language.lower():
                return 'México'
            elif 'ar' in accept_language.lower():
                return 'Argentina'
            elif 'pe' in accept_language.lower():
                return 'Perú'
            elif 'cl' in accept_language.lower():
                return 'Chile'
            else:
                return 'América Latina'
        elif 'en' in accept_language.lower():
            return 'Internacional'
        else:
            return 'Ubicación detectada automáticamente'