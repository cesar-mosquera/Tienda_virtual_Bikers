from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado con roles específicos para Aura Bikers.
    Roles: Cliente, Vendedor, Bodeguero, Administrador
    """
    
    class Rol(models.TextChoices):
        CLIENTE = 'cliente', 'Cliente'
        VENDEDOR = 'vendedor', 'Vendedor'
        BODEGUERO = 'bodeguero', 'Bodeguero'
        ADMIN = 'admin', 'Administrador'
    
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.CLIENTE,
        verbose_name='Rol'
    )
    
    # Campos específicos para clientes (datos de facturación)
    cedula = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Cédula',
        help_text='Número de identificación del cliente'
    )
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección',
        help_text='Dirección de facturación/envío'
    )
    celular = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Celular',
        help_text='Número de contacto'
    )
    
    esta_activo = models.BooleanField(
        default=True,
        verbose_name='Está activo'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    @property
    def es_cliente(self):
        return self.rol == self.Rol.CLIENTE
    
    @property
    def es_vendedor(self):
        return self.rol == self.Rol.VENDEDOR
    
    @property
    def es_bodeguero(self):
        return self.rol == self.Rol.BODEGUERO
    
    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN
