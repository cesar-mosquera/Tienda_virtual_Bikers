from django.db import models
from django.conf import settings
from productos.models import Bicicleta


class IngresoStock(models.Model):
    """
    Modelo para registrar ingresos de inventario.
    El bodeguero confirma la recepción de nuevas unidades.
    """
    
    bicicleta = models.ForeignKey(
        Bicicleta,
        on_delete=models.PROTECT,
        related_name='ingresos_stock',
        verbose_name='Bicicleta'
    )
    cantidad = models.PositiveIntegerField(
        verbose_name='Cantidad Ingresada'
    )
    confirmado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Confirmado Por'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Ingreso'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas/Observaciones'
    )
    
    class Meta:
        verbose_name = 'Ingreso de Stock'
        verbose_name_plural = 'Ingresos de Stock'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.cantidad}x {self.bicicleta.modelo} - {self.fecha.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Al guardar, actualizar el stock de la bicicleta
        if not self.pk:  # Solo en creación
            self.bicicleta.stock += self.cantidad
            self.bicicleta.save(update_fields=['stock'])
        super().save(*args, **kwargs)


class ProductoDanado(models.Model):
    """
    Modelo para registrar productos dañados.
    El bodeguero documenta el daño con foto de evidencia.
    """
    
    class Motivo(models.TextChoices):
        TRANSPORTE = 'transporte', 'Daño en Transporte'
        ALMACENAMIENTO = 'almacenamiento', 'Daño en Almacenamiento'
        DEFECTO_FABRICA = 'defecto_fabrica', 'Defecto de Fábrica'
        EXHIBICION = 'exhibicion', 'Daño en Exhibición'
        OTRO = 'otro', 'Otro'
    
    bicicleta = models.ForeignKey(
        Bicicleta,
        on_delete=models.PROTECT,
        related_name='reportes_dano',
        verbose_name='Bicicleta'
    )
    motivo_tipo = models.CharField(
        max_length=20,
        choices=Motivo.choices,
        default=Motivo.OTRO,
        verbose_name='Tipo de Daño'
    )
    motivo_descripcion = models.TextField(
        verbose_name='Descripción del Daño'
    )
    foto_evidencia = models.ImageField(
        upload_to='productos_danados/',
        verbose_name='Foto de Evidencia'
    )
    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Reportado Por'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del Reporte'
    )
    cantidad_afectada = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad Afectada'
    )
    resuelto = models.BooleanField(
        default=False,
        verbose_name='Resuelto'
    )
    notas_resolucion = models.TextField(
        blank=True,
        verbose_name='Notas de Resolución'
    )
    
    class Meta:
        verbose_name = 'Producto Dañado'
        verbose_name_plural = 'Productos Dañados'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.bicicleta.modelo} - {self.get_motivo_tipo_display()} - {self.fecha.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Al reportar daño, reducir stock
        if not self.pk:  # Solo en creación
            if self.bicicleta.stock >= self.cantidad_afectada:
                self.bicicleta.stock -= self.cantidad_afectada
                self.bicicleta.save(update_fields=['stock'])
        super().save(*args, **kwargs)


class ConfirmacionDespacho(models.Model):
    """
    Modelo para que el bodeguero confirme el despacho de pedidos.
    """
    
    pedido = models.OneToOneField(
        'pedidos.Pedido',
        on_delete=models.CASCADE,
        related_name='confirmacion_despacho',
        verbose_name='Pedido'
    )
    confirmado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Confirmado Por'
    )
    fecha_confirmacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Confirmación'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        verbose_name = 'Confirmación de Despacho'
        verbose_name_plural = 'Confirmaciones de Despacho'
        ordering = ['-fecha_confirmacion']
    
    def __str__(self):
        return f"Despacho Pedido #{self.pedido.pk} - {self.fecha_confirmacion.strftime('%Y-%m-%d %H:%M')}"
