from django.db import models


class Bicicleta(models.Model):
    """
    Modelo para el catálogo de bicicletas premium de Aura Bikers.
    Incluye bicicletas de media y alta gama, tipo Ruta y MTB.
    """
    
    class Gama(models.TextChoices):
        MEDIA = 'media', 'Media Gama'
        ALTA = 'alta', 'Alta Gama'
    
    class Tipo(models.TextChoices):
        RUTA = 'ruta', 'Ruta'
        MTB = 'mtb', 'MTB (Mountain Bike)'
    
    class MedidaMarco(models.TextChoices):
        XS = 'xs', 'XS (Extra Small)'
        S = 's', 'S (Small)'
        M = 'm', 'M (Medium)'
        L = 'l', 'L (Large)'
        XL = 'xl', 'XL (Extra Large)'
    
    marca = models.CharField(
        max_length=100,
        verbose_name='Marca'
    )
    modelo = models.CharField(
        max_length=100,
        verbose_name='Modelo'
    )
    gama = models.CharField(
        max_length=10,
        choices=Gama.choices,
        verbose_name='Gama'
    )
    tipo = models.CharField(
        max_length=10,
        choices=Tipo.choices,
        verbose_name='Tipo'
    )
    medida_marco = models.CharField(
        max_length=5,
        choices=MedidaMarco.choices,
        verbose_name='Medida del Marco'
    )
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio de Venta'
    )
    costo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Costo de Adquisición',
        help_text='Costo sugerido para cálculo de margen de ganancia'
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Stock Disponible'
    )
    imagen = models.ImageField(
        upload_to='bicicletas/',
        blank=True,
        null=True,
        verbose_name='Imagen'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Permite ocultar productos sin eliminarlos'
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
        verbose_name = 'Bicicleta'
        verbose_name_plural = 'Bicicletas'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.get_gama_display()}"
    
    @property
    def margen_ganancia(self):
        """Calcula el margen de ganancia en porcentaje."""
        if self.costo and self.costo > 0:
            return ((self.precio - self.costo) / self.costo) * 100
        return 0
    
    @property
    def ganancia_unitaria(self):
        """Calcula la ganancia por unidad vendida."""
        return self.precio - self.costo
    
    @property
    def disponible(self):
        """Indica si hay stock disponible."""
        return self.stock > 0 and self.activo
