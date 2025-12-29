from django.contrib import admin
from .models import Pedido, DetallePedido, HistorialEstadoPedido


class DetallePedidoInline(admin.TabularInline):
    """Inline para ver detalles del pedido."""
    model = DetallePedido
    extra = 1
    readonly_fields = ('subtotal_display',)
    
    def subtotal_display(self, obj):
        return f"${obj.subtotal:,.2f}" if obj.pk else "-"
    subtotal_display.short_description = 'Subtotal'


class HistorialEstadoInline(admin.TabularInline):
    """Inline para ver historial de estados (solo lectura)."""
    model = HistorialEstadoPedido
    extra = 0
    readonly_fields = ('estado_anterior', 'estado_nuevo', 'cambiado_por', 'fecha', 'notas')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Admin para gestión de pedidos."""
    
    list_display = ('id', 'cliente', 'vendedor', 'estado', 'total', 'creado_por_vendedor', 'fecha_creacion')
    list_filter = ('estado', 'creado_por_vendedor', 'fecha_creacion')
    search_fields = ('cliente__username', 'cliente__cedula', 'vendedor__username')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'total')
    ordering = ('-fecha_creacion',)
    inlines = [DetallePedidoInline, HistorialEstadoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('cliente', 'vendedor', 'estado')
        }),
        ('Entrega', {
            'fields': ('direccion_envio', 'notas')
        }),
        ('Totales', {
            'fields': ('total',)
        }),
        ('Información Adicional', {
            'fields': ('creado_por_vendedor', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HistorialEstadoPedido)
class HistorialEstadoPedidoAdmin(admin.ModelAdmin):
    """Admin para auditoría de cambios de estado."""
    
    list_display = ('pedido', 'estado_anterior', 'estado_nuevo', 'cambiado_por', 'fecha')
    list_filter = ('estado_nuevo', 'fecha')
    search_fields = ('pedido__id', 'cambiado_por__username')
    readonly_fields = ('pedido', 'estado_anterior', 'estado_nuevo', 'cambiado_por', 'fecha', 'notas')
    ordering = ('-fecha',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
