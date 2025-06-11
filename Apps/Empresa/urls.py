from django.urls import path
from . import views

urlpatterns = [
    # URLs de Autenticación
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('check-status/', views.check_account_status, name='check_account_status'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # URLs de Organizaciones
    path('organizations/', views.organization_list, name='organization_list'),
    path('organizations/create/', views.create_organization, name='create_organization'),
    path('organizations/<int:pk>/', views.organization_detail, name='organization_detail'),
    path('organizations/<int:pk>/edit/', views.edit_organization, name='edit_organization'),
    path('organizations/<int:pk>/delete/', views.delete_organization, name='delete_organization'),
    
    # URLs de Categorías
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/toggle/', views.toggle_category_status, name='toggle_category_status'),
    
    # URLs de Gestión de Usuarios (Solo Staff)
    path('admin/pending-users/', views.pending_users_view, name='pending_users'),
    path('admin/activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    
    # URLs de Perfil y Feed
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('feed/', views.public_feed, name='public_feed'),
    path('dashboard/feed/', views.dashboard_feed, name='dashboard_feed'),
] 