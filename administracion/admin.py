from django.contrib import admin
from .models import PQRS, Promocion


@admin.register(PQRS)
class PQRSAdmin(admin.ModelAdmin):
    """Admin para gestión de PQRS."""
    
    list_display = ('id', 'tipo', 'asunto', 'cliente', 'estado', 'fecha_creacion', 'resuelto_por')
    list_filter = ('tipo', 'estado', 'fecha_creacion')
    search_fields = ('asunto', 'descripcion', 'cliente__username')
    readonly_fields = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)
    list_editable = ('estado',)
    
    fieldsets = (
        ('Caso', {
            'fields': ('cliente', 'tipo', 'asunto', 'descripcion')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_creacion')
        }),
        ('Resolución', {
            'fields': ('respuesta', 'resuelto_por', 'fecha_resolucion')
        }),
    )


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    """Admin para gestión de promociones."""
    
    list_display = ('nombre', 'descuento', 'fecha_inicio', 'fecha_fin', 'activa', 'aplica_a_todas', 'esta_vigente_display')
    list_filter = ('activa', 'aplica_a_todas', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'descripcion')
    filter_horizontal = ('bicicletas',)
    readonly_fields = ('fecha_creacion', 'esta_vigente_display')
    ordering = ('-fecha_inicio',)
    list_editable = ('activa',)
    
    fieldsets = (
        ('Información de la Promoción', {
            'fields': ('nombre', 'descripcion', 'descuento')
        }),
        ('Vigencia', {
            'fields': ('fecha_inicio', 'fecha_fin', 'activa', 'esta_vigente_display')
        }),
        ('Productos Aplicables', {
            'fields': ('aplica_a_todas', 'bicicletas')
        }),
        ('Auditoría', {
            'fields': ('creada_por', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    def esta_vigente_display(self, obj):
        return "✅ Sí" if obj.esta_vigente else "❌ No"
    esta_vigente_display.short_description = '¿Está Vigente?'
