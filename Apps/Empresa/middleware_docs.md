# 🛡️ ActiveUserMiddleware - Documentación Completa

## 📋 ¿Qué es el ActiveUserMiddleware?

El `ActiveUserMiddleware` es un middleware personalizado que **verifica automáticamente** si un usuario logueado sigue estando activo en **cada petición HTTP**. Si el usuario ha sido desactivado por un administrador, será **deslogueado automáticamente** y redirigido al login.

## ⚙️ Configuración (YA ACTIVADO)

El middleware ya está configurado en `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'Apps.Empresa.middleware.ActiveUserMiddleware',  # ← AQUÍ ESTÁ
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

## 🔄 ¿Cómo Funciona?

### 1. **En Cada Petición HTTP**
```python
Usuario logueado → Middleware verifica is_active → Continúa o Desloguea
```

### 2. **Si Usuario Está Activo**
```python
✅ La petición continúa normalmente
✅ El usuario puede navegar sin problemas
```

### 3. **Si Usuario Está Inactivo**
```python
❌ Logout automático
❌ Mensaje de error informativo
❌ Redirección al login
```

## 🎯 URLs Excluidas (No Verificadas)

El middleware **NO verifica** estas URLs para evitar loops infinitos:

```python
excluded_urls = [
    '/login/',      # Página de login
    '/admin/',      # Admin de Django
]
```

## 🚀 Ejemplo de Funcionamiento

### Escenario: Usuario Activo Navegando
```
1. Usuario logueado navega a /dashboard/
2. Middleware verifica: user.is_active = True
3. ✅ Petición continúa normalmente
4. Usuario ve el dashboard
```

### Escenario: Administrador Desactiva Usuario
```
1. Admin va a /admin/auth/user/ y desactiva usuario
2. Usuario (aún logueado) navega a /organizations/
3. Middleware verifica: user.is_active = False
4. ❌ Logout automático
5. Mensaje: "Hola username, tu cuenta ha sido desactivada..."
6. Redirección a /login/
```

## 📝 Mensajes del Sistema

### Mensaje de Desactivación
```
"Hola {username}, tu cuenta ha sido desactivada. 
Has sido desconectado automáticamente. 
Contacta al administrador para más información."
```

## 🔧 Personalización Avanzada

### Agregar URLs Excluidas
Si quieres excluir más URLs, edita `middleware.py`:

```python
excluded_urls = [
    reverse('login'),
    '/admin/',
    '/api/',        # ← Agregar API
    '/public/',     # ← Agregar páginas públicas
]
```

### Activar Middleware Adicional
Para mayor seguridad, descomenta en `settings.py`:

```python
'Apps.Empresa.middleware.SecureSessionMiddleware',  # Verificación de integridad
```

## 🧪 Cómo Probar el Middleware

### Prueba Manual:
1. **Crear usuario de prueba**:
   ```bash
   python manage.py createsuperuser
   ```

2. **Loguearse con el usuario**

3. **En otra ventana, ir al admin**:
   - Ve a `/admin/auth/user/`
   - Encuentra tu usuario
   - Desmarca "Activo"
   - Guarda

4. **En la ventana original**:
   - Navega a cualquier página
   - ✅ Deberías ser deslogueado automáticamente

### Prueba Programática:
```python
# En Django shell
from django.contrib.auth.models import User
user = User.objects.get(username='tu_usuario')
user.is_active = False
user.save()
# Ahora navega en el navegador
```

## ⚡ Rendimiento

### Impacto Mínimo:
- ✅ Solo una verificación booleana por petición
- ✅ No consultas adicionales a la base de datos
- ✅ Ejecución en microsegundos

### Optimización:
- El middleware usa `request.user.is_active` (ya cargado)
- No hace consultas SQL adicionales
- Muy eficiente para producción

## 🚨 Casos de Uso Importantes

### 1. **Empleado Despedido**
```
Admin desactiva cuenta → Empleado no puede acceder más
```

### 2. **Cuenta Comprometida**
```
Admin desactiva cuenta → Acceso inmediatamente bloqueado
```

### 3. **Suspensión Temporal**
```
Admin desactiva → Usuario bloqueado
Admin reactiva → Usuario puede loguearse nuevamente
```

## 🔒 Seguridad Adicional

### Combinado con Decoradores:
```python
@login_required
@active_user_required  # Verificación adicional en vistas específicas
def sensitive_view(request):
    # Vista sensible
```

### Logs de Seguridad (Opcional):
Puedes agregar logging al middleware:

```python
import logging
logger = logging.getLogger(__name__)

# En el middleware:
logger.warning(f"Usuario inactivo deslogueado: {username}")
```

## ✅ Estado Actual

- ✅ **Middleware configurado** en settings.py
- ✅ **Funcionando automáticamente** en cada petición
- ✅ **Sin errores** de configuración
- ✅ **Listo para producción**

## 🎊 Resultado Final

**¡Tu aplicación ahora tiene seguridad automática de usuarios inactivos!**

- 🛡️ **Protección automática** en cada página
- ⚡ **Respuesta inmediata** a desactivaciones
- 🔄 **Sin intervención manual** requerida
- 📱 **Funciona en todas las vistas** automáticamente

**El middleware está ACTIVO y funcionando. ¡Tu aplicación es más segura ahora!** 🚀 