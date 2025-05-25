from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserProfile(models.Model):
    user= models.OneToOneField(User,related_name="profile",on_delete=models.CASCADE)
    image=models.CharField(max_length=100,null=True)
    first_name=models.CharField(max_length=30,blank=True,null=True)
    last_name=models.CharField(max_length=30,blank=True,null=True)
    #language=models.CharField(max_length=5, default='es-es')
    email=models.CharField(max_length=50)
    def __str__(self):              # __unicode__ on Python 2
        return_name = str(self.user.id.__str__()+'_user_profile')
        return return_name

class Organization(models.Model):
    name=models.CharField(max_length=50) #
    logo=models.ImageField(upload_to="uploaded/img/organization_logos/",blank=True)
    type=models.CharField(max_length=50)#
    website=models.CharField(max_length=80) #
    phone=models.CharField(max_length=50)
    nit=models.CharField(max_length=20)
    owner=models.OneToOneField(UserProfile,related_name="organization",blank=True, null=True,on_delete=models.CASCADE)
    @staticmethod
    def getCropAttribute():
        return "logo"
    @staticmethod
    def getCropPath():
        return "organization_logos/"
