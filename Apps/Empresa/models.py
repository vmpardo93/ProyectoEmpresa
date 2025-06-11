from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploaded/img/profile_photos/", null=True, blank=True)
    
    # Campos adicionales específicos del perfil (no duplicados de User)
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="Biografía",
                          help_text="Descripción personal o profesional")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ubicación")
    
    # Campos de configuración del usuario
    language = models.CharField(max_length=5, default='es-es', verbose_name="Idioma")
    receive_notifications = models.BooleanField(default=True, verbose_name="Recibir notificaciones")
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def get_image_url(self):
        if self.image:
            return self.image.url
        return None
    
    @property
    def full_name(self):
        """Retorna el nombre completo del usuario desde el modelo User"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def display_name(self):
        """Retorna el nombre para mostrar: nombre completo o username"""
        if self.user.first_name:
            return self.full_name
        return self.user.username

class Organization(models.Model):
    name=models.CharField(max_length=50) #
    logo=models.ImageField(upload_to="uploaded/img/organization_logos/",blank=True)
    type=models.CharField(max_length=50)#
    website=models.CharField(max_length=80) #
    phone=models.CharField(max_length=50)
    nit=models.CharField(max_length=20)
    services = models.CharField(max_length=200, blank=True, null=True, help_text="Ingresa los servicios separados por comas (ej: Consultoría, Desarrollo, Marketing)")
    owner=models.ForeignKey(UserProfile, related_name="organizations", on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category', blank=True, verbose_name="Categorías", 
                                      help_text="Selecciona las categorías que aplican a esta organización")
    
    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @staticmethod
    def getCropAttribute():
        return "logo"
    @staticmethod
    def getCropPath():
        return "organization_logos/"

    def get_services_list(self):
        """Retorna la lista de servicios como una lista de strings"""
        if self.services:
            return [service.strip() for service in self.services.split(',')]
        return []
    
    def get_categories_list(self):
        """Retorna la lista de categorías activas asociadas"""
        return self.categories.filter(status=True)
    
    def get_categories_display(self):
        """Retorna las categorías como texto para mostrar en el admin"""
        categories = self.get_categories_list()
        if categories.exists():
            return ', '.join([cat.name for cat in categories])
        return 'Sin categorías'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción", 
                                 help_text="Descripción detallada de la categoría")
    status = models.BooleanField(default=True, verbose_name="Estado", 
                               help_text="Indica si la categoría está activa o inactiva")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías" 
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_status_display_html(self):
        """Retorna el estado con formato HTML para mostrar en el admin"""
        if self.status:
            return '<span style="color: green; font-weight: bold;">✓ Activa</span>'
        else:
            return '<span style="color: red; font-weight: bold;">✗ Inactiva</span>'

    @property
    def status_text(self):
        """Retorna el estado como texto"""
        return "Activa" if self.status else "Inactiva"
