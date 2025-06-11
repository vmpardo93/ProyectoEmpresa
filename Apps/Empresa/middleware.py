from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

class ActiveUserMiddleware:
    """
    Middleware que verifica automáticamente si un usuario logueado sigue activo.
    Si el usuario está inactivo, lo desloguea automáticamente.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # URLs que no requieren verificación de usuario activo
        excluded_urls = [
            reverse('login'),
            reverse('signup'),  # Excluir página de registro
            '/admin/',  # Excluir admin de Django
            '/api/',    # Excluir APIs (si tienes)
            '/public/', # Excluir páginas públicas (si tienes)
            # '/logout/', # Ya no necesario, logout es bueno verificar
            # Agregar más URLs aquí si necesitas
        ]
        
        # Verificar si el usuario está autenticado y la URL no está excluida
        if (request.user.is_authenticated and 
            not any(request.path.startswith(url) for url in excluded_urls)):
            
            # Verificar si el usuario está activo
            if not request.user.is_active:
                # Guardar el username antes del logout
                username = request.user.username
                
                # Desloguear automáticamente al usuario inactivo
                logout(request)
                
                # Agregar mensaje de error
                messages.error(request, 
                    f"Hola {username}, tu cuenta ha sido desactivada. "
                    "Has sido desconectado automáticamente. "
                    "Contacta al administrador para más información."
                )
                
                # Redirigir al login
                return redirect('login')
        
        response = self.get_response(request)
        return response

class SecureSessionMiddleware:
    """
    Middleware adicional para verificar la integridad de la sesión
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Verificar si hay datos inconsistentes en la sesión
        if request.user.is_authenticated:
            # Verificar que el usuario en la sesión existe en la base de datos
            try:
                user = request.user
                # Forzar una consulta a la base de datos para verificar que el usuario existe
                user.refresh_from_db()
                
                # Verificar campos básicos del usuario
                if not user.username:
                    logout(request)
                    messages.error(request, "Sesión inválida. Por favor inicia sesión nuevamente.")
                    return redirect('login')
                    
            except Exception:
                # Si hay cualquier error, cerrar sesión por seguridad
                logout(request)
                messages.error(request, "Error en la sesión. Por favor inicia sesión nuevamente.")
                return redirect('login')
        
        response = self.get_response(request)
        return response 