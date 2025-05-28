from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('organizations/', views.organization_list, name='organization_list'),
    path('organizations/create/', views.create_organization, name='create_organization'),
    path('organizations/<int:pk>/edit/', views.edit_organization, name='edit_organization'),
    path('organizations/<int:pk>/delete/', views.delete_organization, name='delete_organization'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('feed/', views.public_feed, name='public_feed'),
    path('dashboard/feed/', views.dashboard_feed, name='dashboard_feed'),
] 