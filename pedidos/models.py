from django.db import models
from django.conf import settings
from productos.models import Bicicleta


class Pedido(models.Model):
    """
    Modelo para gestión de pedidos con flujo de estados.
    Estados: Pendiente -> Confirmado -> Despachado -> En Camino -> Entregado
    """
    
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADO = 'confirmado', 'Confirmado'
        DESPACHADO = 'despachado', 'Despachado'
        EN_CAMINO = 'en_camino', 'En Camino'
        ENTREGADO = 'entregado', 'Entregado'
        CANCELADO = 'cancelado', 'Cancelado'
    
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos_cliente',
        verbose_name='Cliente'
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_vendedor',
        verbose_name='Vendedor Asignado'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado'
    )
    direccion_envio = models.TextField(
        verbose_name='Dirección de Envío'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Total'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    creado_por_vendedor = models.BooleanField(
        default=False,
        verbose_name='Creado por Vendedor',
        help_text='Indica si es una venta telefónica'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente.username} - {self.get_estado_display()}"
    
    def calcular_total(self):
        """Calcula el total sumando todos los detalles del pedido."""
        total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.total = total
        self.save(update_fields=['total'])
        return total
    
    def cambiar_estado(self, nuevo_estado, usuario):
        """
        Cambia el estado del pedido y registra en el historial.
        """
        estado_anterior = self.estado
        self.estado = nuevo_estado
        self.save(update_fields=['estado'])
        
        # Registrar en historial de auditoría
        HistorialEstadoPedido.objects.create(
            pedido=self,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            cambiado_por=usuario,
            notas=f"Cambio de {estado_anterior} a {nuevo_estado}"
        )
        return True


class DetallePedido(models.Model):
    """
    Detalle de cada producto en un pedido.
    """
    
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Pedido'
    )
    bicicleta = models.ForeignKey(
        Bicicleta,
        on_delete=models.PROTECT,
        verbose_name='Bicicleta'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio Unitario',
        help_text='Precio al momento de la venta'
    )
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'
    
    def __str__(self):
        return f"{self.cantidad}x {self.bicicleta.modelo} - Pedido #{self.pedido.pk}"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def save(self, *args, **kwargs):
        # Si no se ha establecido precio, usar el precio actual de la bicicleta
        if not self.precio_unitario:
            self.precio_unitario = self.bicicleta.precio
        super().save(*args, **kwargs)


class HistorialEstadoPedido(models.Model):
    """
    Modelo de auditoría para rastrear cambios de estado en pedidos.
    Permite auditar quién y cuándo cambió el estado de un pedido.
    """
    
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='historial_estados',
        verbose_name='Pedido'
    )
    estado_anterior = models.CharField(
        max_length=20,
        choices=Pedido.Estado.choices,
        verbose_name='Estado Anterior'
    )
    estado_nuevo = models.CharField(
        max_length=20,
        choices=Pedido.Estado.choices,
        verbose_name='Estado Nuevo'
    )
    cambiado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Cambiado Por'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del Cambio'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Pedido #{self.pedido.pk}: {self.estado_anterior} -> {self.estado_nuevo}"
