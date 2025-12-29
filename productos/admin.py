from django.contrib import admin
from .models import Bicicleta


@admin.register(Bicicleta)
class BicicletaAdmin(admin.ModelAdmin):
    """Admin para gestión del catálogo de bicicletas."""
    
    list_display = ('marca', 'modelo', 'gama', 'tipo', 'medida_marco', 'precio', 'stock', 'activo')
    list_filter = ('gama', 'tipo', 'medida_marco', 'activo', 'marca')
    search_fields = ('marca', 'modelo', 'descripcion')
    list_editable = ('precio', 'stock', 'activo')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'margen_ganancia_display', 'ganancia_unitaria_display')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('marca', 'modelo', 'descripcion', 'imagen')
        }),
        ('Clasificación', {
            'fields': ('gama', 'tipo', 'medida_marco')
        }),
        ('Precios y Stock', {
            'fields': ('precio', 'costo', 'stock', 'margen_ganancia_display', 'ganancia_unitaria_display')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def margen_ganancia_display(self, obj):
        return f"{obj.margen_ganancia:.2f}%"
    margen_ganancia_display.short_description = 'Margen de Ganancia'
    
    def ganancia_unitaria_display(self, obj):
        return f"${obj.ganancia_unitaria:,.2f}"
    ganancia_unitaria_display.short_description = 'Ganancia por Unidad'
