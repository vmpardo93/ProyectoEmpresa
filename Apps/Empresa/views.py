from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .models import UserProfile, Organization, Category
from .forms import OrganizationForm, UserProfileForm, CategoryForm, SignupForm

# Create your views here.

def check_user_active(user):
    """
    Verifica si un usuario está activo.
    Si no está activo, lo desloguea y levanta una excepción.
    """
    if not user.is_active:
        return False
    return True

def active_user_required(view_func):
    """
    Decorador personalizado que verifica si el usuario está activo.
    Si no está activo, lo desloguea y redirige al login.
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_active:
                logout(request)
                messages.error(request, 
                    "Tu cuenta ha sido desactivada. "
                    "Has sido desconectado automáticamente."
                )
                return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def login_view(request):
    # Si el usuario ya está logueado, redirigir al dashboard
    if request.user.is_authenticated:
        messages.info(request, f"Ya tienes una sesión activa, {request.user.username}.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Primero verificamos si el usuario existe y las credenciales son correctas
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Verificar explícitamente si el usuario está activo
                if user.is_active:
                login(request, user)
                    messages.success(request, f"¡Bienvenido {user.username}!")
                return redirect('dashboard')
                else:
                    # Usuario existe pero está inactivo
                    messages.error(request, 
                        "Tu cuenta ha sido desactivada. "
                        "Contacta al administrador para reactivar tu cuenta."
                    )
            else:
                # Credenciales incorrectas o usuario no existe
                messages.error(request, "Usuario o contraseña inválidos.")
        else:
            # Formulario inválido
            messages.error(request, "Por favor corrige los errores en el formulario.")
    
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup_view(request):
    """Vista de registro de nuevos usuarios"""
    # Si el usuario ya está logueado, redirigir al dashboard
    if request.user.is_authenticated:
        messages.info(request, f"Ya tienes una sesión activa, {request.user.username}.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Crear usuario inactivo y perfil
            user = form.save(request=request)
            
            messages.success(
                request,
                f"¡Registro exitoso, {user.first_name}! "
                "Tu cuenta ha sido creada pero está pendiente de activación. "
                "Un administrador revisará tu solicitud y activará tu cuenta pronto. "
                "Recibirás un correo cuando esté lista."
            )
            return redirect('login')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = SignupForm()
    
    context = {
        'form': form,
        'title': 'Registro de Nueva Cuenta'
    }
    return render(request, 'signup.html', context)

@login_required
@active_user_required
def dashboard(request):
    try:
        user_profile = request.user.profile
        organization = user_profile.organizations.first()  # Obtiene la primera organización
        
        # Obtener las 6 organizaciones más recientes
        recent_organizations = Organization.objects.all().order_by('-id')[:6]
        
        context = {
            'user_profile': user_profile,
            'organization': organization,
            'recent_organizations': recent_organizations,
        }
        return render(request, 'dashboard.html', context)
    except UserProfile.DoesNotExist:
        # Si el usuario no tiene perfil, crear uno
        user_profile = UserProfile.objects.create(
            user=request.user
        )
        # Obtener las 6 organizaciones más recientes
        recent_organizations = Organization.objects.all().order_by('-id')[:6]
        
        context = {
            'user_profile': user_profile,
            'organization': None,
            'recent_organizations': recent_organizations,
        }
        return render(request, 'dashboard.html', context)

@login_required
@active_user_required
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
            # Guardar las categorías seleccionadas (relación many-to-many)
            form.save_m2m()
            messages.success(request, "Organización creada exitosamente.")
            return redirect('organization_list')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = OrganizationForm()
    
    return render(request, 'organization/create.html', {'form': form})

@login_required
def edit_organization(request, pk):
    organization = get_object_or_404(Organization, pk=pk, owner=request.user.profile)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES, instance=organization)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.save()
            # Guardar las categorías seleccionadas (relación many-to-many)
            form.save_m2m()
            messages.success(request, "Organización actualizada exitosamente.")
            return redirect('organization_list')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
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
@active_user_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=request.user
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

def public_feed(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    organizations = Organization.objects.all().prefetch_related('categories')
    
    if search_query:
        # Dividir la búsqueda en términos individuales
        search_terms = [term.strip() for term in search_query.split(',')]
        # Inicializar query vacío
        query = Q()
        
        # Agregar cada término a la búsqueda (incluyendo categorías)
        for term in search_terms:
            query |= (
                Q(name__icontains=term) |
                Q(services__icontains=term) |
                Q(type__icontains=term) |
                Q(categories__name__icontains=term)
            )
        
        organizations = organizations.filter(query).distinct()
    
    # Filtrar por categoría específica si se selecciona
    if category_filter:
        organizations = organizations.filter(categories__id=category_filter).distinct()

    # Obtener todas las categorías activas para el filtro
    active_categories = Category.objects.filter(status=True).order_by('name')

    context = {
        'organizations': organizations,
        'search_query': search_query,
        'category_filter': category_filter,
        'active_categories': active_categories,
    }

    # Si el usuario está autenticado, usar el template con sidebar
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile
            organization = user_profile.organizations.first()
            context.update({
                'user_profile': user_profile,
                'organization': organization,
            })
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'organization/public_feed.html', context)

@login_required
def dashboard_feed(request):
    try:
        user_profile = request.user.profile
        organization = user_profile.organizations.first()
        organizations = Organization.objects.all().prefetch_related('categories').order_by('-id')
        
        # Obtener todas las categorías activas para mostrar estadísticas
        active_categories = Category.objects.filter(status=True).order_by('name')
        
        context = {
            'user_profile': user_profile,
            'organization': organization,
            'organizations': organizations,
            'active_categories': active_categories,
        }
        return render(request, 'organization/dashboard_feed.html', context)
    except UserProfile.DoesNotExist:
        return redirect('dashboard')

@login_required 
def category_list(request):
    """Vista para mostrar todas las categorías disponibles"""
    categories = Category.objects.all().order_by('name')
    active_count = categories.filter(status=True).count()
    inactive_count = categories.filter(status=False).count()
    
    context = {
        'categories': categories,
        'active_count': active_count,
        'inactive_count': inactive_count,
    }
    
    # Agregar información del usuario si existe
    try:
        user_profile = request.user.profile
        organization = user_profile.organizations.first()
        context.update({
            'user_profile': user_profile,
            'organization': organization,
        })
    except UserProfile.DoesNotExist:
        pass
    
    return render(request, 'category/list.html', context)

@login_required
def organization_detail(request, pk):
    """Vista para mostrar los detalles de una organización incluyendo sus categorías"""
    organization = get_object_or_404(Organization, pk=pk)
    organization_categories = organization.categories.filter(status=True)
    
    context = {
        'organization': organization,
        'organization_categories': organization_categories,
        'is_owner': request.user.profile == organization.owner if hasattr(request.user, 'profile') else False,
    }
    
    # Agregar información del usuario si existe
    try:
        user_profile = request.user.profile
        user_organization = user_profile.organizations.first()
        context.update({
            'user_profile': user_profile,
            'user_organization': user_organization,
        })
    except UserProfile.DoesNotExist:
        pass
    
    return render(request, 'organization/detail.html', context)

@login_required
def create_category(request):
    """Vista para crear una nueva categoría (solo para staff/superuser)"""
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para crear categorías.")
        return redirect('category_list')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Categoría '{category.name}' creada exitosamente.")
            return redirect('category_list')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Crear Nueva Categoría'
    }
    
    # Agregar información del usuario si existe
    try:
        user_profile = request.user.profile
        organization = user_profile.organizations.first()
        context.update({
            'user_profile': user_profile,
            'organization': organization,
        })
    except UserProfile.DoesNotExist:
        pass
    
    return render(request, 'category/create.html', context)

@login_required
def edit_category(request, pk):
    """Vista para editar una categoría existente (solo para staff/superuser)"""
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para editar categorías.")
        return redirect('category_list')
        
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Categoría '{category.name}' actualizada exitosamente.")
            return redirect('category_list')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': f'Editar Categoría: {category.name}'
    }
    
    # Agregar información del usuario si existe
    try:
        user_profile = request.user.profile
        organization = user_profile.organizations.first()
        context.update({
            'user_profile': user_profile,
            'organization': organization,
        })
    except UserProfile.DoesNotExist:
        pass
    
    return render(request, 'category/edit.html', context)

@login_required
def toggle_category_status(request, pk):
    """Vista para activar/desactivar una categoría (solo para staff/superuser)"""
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para modificar categorías.")
        return redirect('category_list')
    
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.status = not category.status
        category.save()
        
        status_text = "activada" if category.status else "desactivada"
        messages.success(request, f"Categoría '{category.name}' {status_text} exitosamente.")
    
    return redirect('category_list')

def logout_view(request):
    """Vista personalizada de logout con mensaje de confirmación"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f"Has cerrado sesión exitosamente. ¡Hasta pronto, {username}!")
    return redirect('login')

def check_account_status(request):
    """Vista para verificar el estado de la cuenta del usuario actual"""
    if request.user.is_authenticated:
        if not request.user.is_active:
            logout(request)
            messages.error(request, 
                "Tu cuenta ha sido desactivada. "
                "Por favor contacta al administrador."
            )
            return redirect('login')
        else:
            messages.info(request, "Tu cuenta está activa y funcionando correctamente.")
            return redirect('dashboard')
    else:
        messages.info(request, "Debes iniciar sesión para verificar el estado de tu cuenta.")
        return redirect('login')

@login_required
def pending_users_view(request):
    """Vista para que admins vean usuarios pendientes de activación"""
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('dashboard')
    
    # Obtener usuarios inactivos (pendientes de activación)
    pending_users = User.objects.filter(is_active=False).order_by('-date_joined')
    
    context = {
        'pending_users': pending_users,
        'title': 'Usuarios Pendientes de Activación'
    }
    
    # Agregar información del usuario si existe
    try:
        user_profile = request.user.profile
        organization = user_profile.organizations.first()
        context.update({
            'user_profile': user_profile,
            'organization': organization,
        })
    except UserProfile.DoesNotExist:
        pass
    
    return render(request, 'admin/pending_users.html', context)

@login_required
def activate_user(request, user_id):
    """Vista para activar un usuario específico"""
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('dashboard')
    
    user_to_activate = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_to_activate.is_active = True
        user_to_activate.save()
        
        messages.success(
            request, 
            f"Usuario '{user_to_activate.username}' ({user_to_activate.get_full_name()}) "
            "ha sido activado exitosamente."
        )
        
        # TODO: Aquí podrías enviar un email de notificación al usuario
        # send_activation_email(user_to_activate)
    
    return redirect('pending_users')
