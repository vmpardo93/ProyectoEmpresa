from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse
from .models import UserProfile, Organization
from .forms import OrganizationForm, UserProfileForm

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Usuario o contraseña inválidos.")
        else:
            messages.error(request, "Usuario o contraseña inválidos.")
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    try:
        user_profile = request.user.profile
        organization = user_profile.organizations.first()  # Obtiene la primera organización
        
        context = {
            'user_profile': user_profile,
            'organization': organization,
        }
        return render(request, 'dashboard.html', context)
    except UserProfile.DoesNotExist:
        # Si el usuario no tiene perfil, crear uno
        user_profile = UserProfile.objects.create(
            user=request.user,
            email=request.user.email,
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
        context = {
            'user_profile': user_profile,
            'organization': None,
        }
        return render(request, 'dashboard.html', context)

@login_required
def organization_list(request):
    organizations = request.user.profile.organizations.all()
    return render(request, 'organization/list.html', {'organizations': organizations})

@login_required
def create_organization(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.owner = request.user.profile
            organization.save()
            messages.success(request, "Organización creada exitosamente.")
            return redirect('organization_list')
    else:
        form = OrganizationForm()
    
    return render(request, 'organization/create.html', {'form': form})

@login_required
def edit_organization(request, pk):
    organization = get_object_or_404(Organization, pk=pk, owner=request.user.profile)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES, instance=organization)
        if form.is_valid():
            form.save()
            messages.success(request, "Organización actualizada exitosamente.")
            return redirect('organization_list')
    else:
        form = OrganizationForm(instance=organization)
    
    return render(request, 'organization/edit.html', {
        'form': form,
        'organization': organization
    })

@login_required
def delete_organization(request, pk):
    organization = get_object_or_404(Organization, pk=pk, owner=request.user.profile)
    
    if request.method == 'POST':
        organization.delete()
        messages.success(request, "Organización eliminada exitosamente.")
        return redirect('organization_list')
    
    return render(request, 'organization/delete.html', {'organization': organization})

@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=request.user,
            email=request.user.email,
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile/edit.html', {
        'form': form,
        'profile': profile
    })
