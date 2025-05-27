from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User,related_name="profile",on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploaded/img/profile_photos/", null=True, blank=True)
    first_name = models.CharField(max_length=30,blank=True,null=True)
    last_name = models.CharField(max_length=30,blank=True,null=True)
    #language=models.CharField(max_length=5, default='es-es')
    email = models.CharField(max_length=50)
    def __str__(self):              # __unicode__ on Python 2
        return_name = str(self.user.id.__str__()+'_user_profile')
        return return_name

    @property
    def get_image_url(self):
        if self.image:
            return self.image.url
        return None

class Organization(models.Model):
    name=models.CharField(max_length=50) #
    logo=models.ImageField(upload_to="uploaded/img/organization_logos/",blank=True)
    type=models.CharField(max_length=50)#
    website=models.CharField(max_length=80) #
    phone=models.CharField(max_length=50)
    nit=models.CharField(max_length=20)
    services = models.CharField(max_length=200, blank=True, null=True, help_text="Ingresa los servicios separados por comas (ej: Consultoría, Desarrollo, Marketing)")
    owner=models.ForeignKey(UserProfile, related_name="organizations", on_delete=models.CASCADE)
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
