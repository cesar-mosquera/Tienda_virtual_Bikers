from django.shortcuts import render, get_object_or_404
from django.db import models
from .models import Bicicleta


def catalogo(request):
    """Vista del catálogo de bicicletas."""
    # Mostrar TODAS las bicicletas activas (incluso las de stock 0, se muestran como "Agotado")
    bicicletas = Bicicleta.objects.filter(activo=True).order_by('-stock', '-fecha_creacion')
    
    # Obtener marcas únicas para el filtro
    marcas_disponibles = Bicicleta.objects.filter(activo=True).values_list('marca', flat=True).distinct()
    
    # Filtros
    gama = request.GET.get('gama', '')
    tipo = request.GET.get('tipo', '')
    marca = request.GET.get('marca', '')
    busqueda = request.GET.get('q', '')
    
    # Verificar si hay filtros activos
    hay_filtros = bool(gama or tipo or marca or busqueda)
    
    if gama:
        bicicletas = bicicletas.filter(gama=gama)
    if tipo:
        bicicletas = bicicletas.filter(tipo=tipo)
    if marca:
        bicicletas = bicicletas.filter(marca__iexact=marca)
    if busqueda:
        bicicletas = bicicletas.filter(
            models.Q(marca__icontains=busqueda) | 
            models.Q(modelo__icontains=busqueda)
        )
    
    context = {
        'bicicletas': bicicletas,
        'gamas': Bicicleta.Gama.choices,
        'tipos': Bicicleta.Tipo.choices,
        'marcas': marcas_disponibles,
        'hay_filtros': hay_filtros,
        'filtro_gama': gama,
        'filtro_tipo': tipo,
        'filtro_marca': marca,
        'filtro_busqueda': busqueda,
    }
    return render(request, 'productos/catalogo.html', context)


def detalle_bicicleta(request, pk):
    """Vista de detalle de una bicicleta."""
    bicicleta = get_object_or_404(Bicicleta, pk=pk, activo=True)
    return render(request, 'productos/detalle.html', {'bicicleta': bicicleta})
