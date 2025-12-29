from django.contrib import admin
from .models import IngresoStock, ProductoDanado, ConfirmacionDespacho


@admin.register(IngresoStock)
class IngresoStockAdmin(admin.ModelAdmin):
    """Admin para registrar ingresos de inventario."""
    
    list_display = ('bicicleta', 'cantidad', 'confirmado_por', 'fecha')
    list_filter = ('fecha', 'bicicleta__marca')
    search_fields = ('bicicleta__modelo', 'bicicleta__marca', 'notas')
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)
    
    fieldsets = (
        ('Producto', {
            'fields': ('bicicleta', 'cantidad')
        }),
        ('Confirmación', {
            'fields': ('confirmado_por', 'notas')
        }),
        ('Registro', {
            'fields': ('fecha',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductoDanado)
class ProductoDanadoAdmin(admin.ModelAdmin):
    """Admin para gestionar reportes de productos dañados."""
    
    list_display = ('bicicleta', 'motivo_tipo', 'cantidad_afectada', 'reportado_por', 'fecha', 'resuelto')
    list_filter = ('motivo_tipo', 'resuelto', 'fecha')
    search_fields = ('bicicleta__modelo', 'motivo_descripcion')
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)
    list_editable = ('resuelto',)
    
    fieldsets = (
        ('Producto Afectado', {
            'fields': ('bicicleta', 'cantidad_afectada')
        }),
        ('Detalle del Daño', {
            'fields': ('motivo_tipo', 'motivo_descripcion', 'foto_evidencia')
        }),
        ('Reporte', {
            'fields': ('reportado_por', 'fecha')
        }),
        ('Resolución', {
            'fields': ('resuelto', 'notas_resolucion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConfirmacionDespacho)
class ConfirmacionDespachoAdmin(admin.ModelAdmin):
    """Admin para confirmaciones de despacho."""
    
    list_display = ('pedido', 'confirmado_por', 'fecha_confirmacion')
    list_filter = ('fecha_confirmacion',)
    search_fields = ('pedido__id', 'confirmado_por__username')
    readonly_fields = ('fecha_confirmacion',)
    ordering = ('-fecha_confirmacion',)
