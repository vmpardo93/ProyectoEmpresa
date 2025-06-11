from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import UserProfile, Organization, Category

# Configuración para mostrar UserProfile inline con User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    extra = 0
    fields = ('image', 'bio', 'phone', 'location', 'language', 'receive_notifications')

# Configuración personalizada del admin para User
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active_display', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ['username', 'first_name', 'last_name', 'email']
    actions = ['activate_users', 'deactivate_users']
    
    def is_active_display(self, obj):
        """Muestra el estado activo/inactivo con colores"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activo</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactivo</span>'
            )
    is_active_display.short_description = 'Estado'
    is_active_display.admin_order_field = 'is_active'
    
    def activate_users(self, request, queryset):
        """Acción para activar usuarios seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} usuario(s) han sido activados.')
    activate_users.short_description = "Activar usuarios seleccionados"
    
    def deactivate_users(self, request, queryset):
        """Acción para desactivar usuarios seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} usuario(s) han sido desactivados.')
    deactivate_users.short_description = "Desactivar usuarios seleccionados"

# Configuración del admin para UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_full_name', 'get_email', 'phone', 'location', 'get_user_status')
    list_filter = ('user__is_active', 'user__date_joined', 'language', 'receive_notifications')
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone', 'location']
    readonly_fields = ('user',)
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Usuario'
    get_username.admin_order_field = 'user__username'
    
    def get_full_name(self, obj):
        """Muestra el nombre completo del usuario"""
        return obj.full_name
    get_full_name.short_description = 'Nombre Completo'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_email(self, obj):
        """Muestra el email del usuario"""
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_user_status(self, obj):
        """Muestra el estado del usuario asociado"""
        if obj.user.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activo</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactivo</span>'
            )
    get_user_status.short_description = 'Estado del Usuario'
    get_user_status.admin_order_field = 'user__is_active'

# Configuración del admin para Organization
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'website', 'phone', 'nit', 'get_categories_count', 'get_owner_username', 'get_owner_status')
    list_filter = ('type', 'categories', 'owner__user__is_active')
    search_fields = ['name', 'type', 'website', 'nit', 'owner__user__username', 'categories__name']
    readonly_fields = ('get_services_display', 'get_categories_display_readonly')
    filter_horizontal = ('categories',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'type', 'logo', 'website', 'phone', 'nit')
        }),
        ('Servicios y Categorías', {
            'fields': ('services', 'categories')
        }),
        ('Propietario', {
            'fields': ('owner',)
        }),
        ('Información de Solo Lectura', {
            'fields': ('get_services_display', 'get_categories_display_readonly'),
            'classes': ('collapse',)
        }),
    )
    
    def get_owner_username(self, obj):
        return obj.owner.user.username
    get_owner_username.short_description = 'Propietario'
    get_owner_username.admin_order_field = 'owner__user__username'
    
    def get_owner_status(self, obj):
        """Muestra el estado del propietario"""
        if obj.owner.user.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activo</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactivo</span>'
            )
    get_owner_status.short_description = 'Estado del Propietario'
    get_owner_status.admin_order_field = 'owner__user__is_active'
    
    def get_services_display(self, obj):
        """Muestra los servicios de forma legible"""
        services = obj.get_services_list()
        if services:
            return ', '.join(services)
        return 'Sin servicios'
    get_services_display.short_description = 'Servicios'
    
    def get_categories_count(self, obj):
        """Muestra el número de categorías asociadas"""
        count = obj.categories.count()
        active_count = obj.categories.filter(status=True).count()
        if count > 0:
            return format_html(
                f'<span style="font-weight: bold;">{active_count}/{count}</span> '
                f'<span style="color: gray; font-size: 11px;">(activas/total)</span>'
            )
        return format_html('<span style="color: gray;">Sin categorías</span>')
    get_categories_count.short_description = 'Categorías'
    
    def get_categories_display_readonly(self, obj):
        """Muestra las categorías para solo lectura con estado"""
        categories = obj.categories.all()
        if categories.exists():
            display_list = []
            for cat in categories:
                status_color = "green" if cat.status else "red"
                status_symbol = "✓" if cat.status else "✗"
                display_list.append(
                    f'<span style="color: {status_color};">{status_symbol} {cat.name}</span>'
                )
            return format_html('<br>'.join(display_list))
        return 'Sin categorías asignadas'
    get_categories_display_readonly.short_description = 'Categorías Asignadas'

# Configuración del admin para Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'status_display', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ['name', 'description']
    actions = ['activate_categories', 'deactivate_categories']
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'description', 'status')
        }),
        ('Información de Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def description_short(self, obj):
        """Muestra una versión corta de la descripción"""
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_short.short_description = 'Descripción'
    
    def status_display(self, obj):
        """Muestra el estado con colores"""
        if obj.status:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activa</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactiva</span>'
            )
    status_display.short_description = 'Estado'
    status_display.admin_order_field = 'status'
    
    def activate_categories(self, request, queryset):
        """Acción para activar categorías seleccionadas"""
        updated = queryset.update(status=True)
        self.message_user(request, f'{updated} categoría(s) han sido activadas.')
    activate_categories.short_description = "Activar categorías seleccionadas"
    
    def deactivate_categories(self, request, queryset):
        """Acción para desactivar categorías seleccionadas"""
        updated = queryset.update(status=False)
        self.message_user(request, f'{updated} categoría(s) han sido desactivadas.')
    deactivate_categories.short_description = "Desactivar categorías seleccionadas"

# Desregistrar el UserAdmin original y registrar el personalizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Personalizar títulos del admin
admin.site.site_header = "Administración de ProjectOpp"
admin.site.site_title = "ProjectOpp Admin"
admin.site.index_title = "Panel de Administración"
