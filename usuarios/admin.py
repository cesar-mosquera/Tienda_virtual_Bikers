from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin personalizado para el modelo CustomUser."""
    
    list_display = ('username', 'email', 'rol', 'cedula', 'celular', 'esta_activo', 'date_joined')
    list_filter = ('rol', 'esta_activo', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'cedula', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Aura Bikers', {
            'fields': ('rol', 'cedula', 'direccion', 'celular', 'esta_activo')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Aura Bikers', {
            'fields': ('rol', 'cedula', 'direccion', 'celular')
        }),
    )
