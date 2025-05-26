"""ProjectOpp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from Apps.Empresa.views import (
    login_view, dashboard, create_organization,
    organization_list, edit_organization, delete_organization,
    edit_profile
)
from home.views import about_us
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', about_us, name='home'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('organizations/', organization_list, name='organization_list'),
    path('organization/create/', create_organization, name='create_organization'),
    path('organization/<int:pk>/edit/', edit_organization, name='edit_organization'),
    path('organization/<int:pk>/delete/', delete_organization, name='delete_organization'),
    path('profile/edit/', edit_profile, name='edit_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configuración adicional para el logout en producción
if not settings.DEBUG:
    urlpatterns = [path('', about_us, name='home'),
                  path('login/', login_view, name='login'),
                  path('dashboard/', dashboard, name='dashboard'),
                  path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),  # URL absoluta
                  path('organizations/', organization_list, name='organization_list'),
                  path('organization/create/', create_organization, name='create_organization'),
                  path('organization/<int:pk>/edit/', edit_organization, name='edit_organization'),
                  path('organization/<int:pk>/delete/', delete_organization, name='delete_organization'),
                  path('profile/edit/', edit_profile, name='edit_profile'),
                  path('admin/', admin.site.urls),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
