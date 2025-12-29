from django.db import models
from django.conf import settings
from productos.models import Bicicleta


class PQRS(models.Model):
    """
    Modelo para Peticiones, Quejas, Reclamos y Sugerencias.
    Los clientes pueden enviar casos y el administrador los resuelve.
    """
    
    class Tipo(models.TextChoices):
        PETICION = 'peticion', 'Petición'
        QUEJA = 'queja', 'Queja'
        RECLAMO = 'reclamo', 'Reclamo'
        SUGERENCIA = 'sugerencia', 'Sugerencia'
    
    class Estado(models.TextChoices):
        ABIERTO = 'abierto', 'Abierto'
        EN_PROCESO = 'en_proceso', 'En Proceso'
        RESUELTO = 'resuelto', 'Resuelto'
    
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pqrs',
        verbose_name='Cliente'
    )
    tipo = models.CharField(
        max_length=15,
        choices=Tipo.choices,
        verbose_name='Tipo'
    )
    asunto = models.CharField(
        max_length=200,
        verbose_name='Asunto'
    )
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.ABIERTO,
        verbose_name='Estado'
    )
    respuesta = models.TextField(
        blank=True,
        verbose_name='Respuesta del Administrador'
    )
    resuelto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pqrs_resueltos',
        verbose_name='Resuelto Por'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_resolucion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Resolución'
    )
    
    class Meta:
        verbose_name = 'PQRS'
        verbose_name_plural = 'PQRS'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.asunto} ({self.get_estado_display()})"


class Promocion(models.Model):
    """
    Modelo para gestionar promociones por fechas especiales.
    Permite aplicar descuentos a productos específicos.
    """
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre de la Promoción'
    )
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Porcentaje de Descuento',
        help_text='Porcentaje de descuento (ej: 15.00 para 15%)'
    )
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    fecha_fin = models.DateField(
        verbose_name='Fecha de Fin'
    )
    activa = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    bicicletas = models.ManyToManyField(
        Bicicleta,
        blank=True,
        related_name='promociones',
        verbose_name='Bicicletas Aplicables'
    )
    aplica_a_todas = models.BooleanField(
        default=False,
        verbose_name='Aplica a Todas',
        help_text='Si está activo, aplica a todo el catálogo'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Creada Por'
    )
    
    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.nombre} - {self.descuento}% ({self.fecha_inicio} a {self.fecha_fin})"
    
    @property
    def esta_vigente(self):
        """Indica si la promoción está vigente actualmente."""
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.activa and self.fecha_inicio <= hoy <= self.fecha_fin
