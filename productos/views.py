from django.shortcuts import render, get_object_or_404
from .models import Bicicleta


def catalogo(request):
    """Vista del catálogo de bicicletas."""
    bicicletas = Bicicleta.objects.filter(activo=True)
    
    # Filtros
    gama = request.GET.get('gama')
    tipo = request.GET.get('tipo')
    marca = request.GET.get('marca')
    
    if gama:
        bicicletas = bicicletas.filter(gama=gama)
    if tipo:
        bicicletas = bicicletas.filter(tipo=tipo)
    if marca:
        bicicletas = bicicletas.filter(marca__icontains=marca)
    
    context = {
        'bicicletas': bicicletas,
        'gamas': Bicicleta.Gama.choices,
        'tipos': Bicicleta.Tipo.choices,
    }
    return render(request, 'productos/catalogo.html', context)


def detalle_bicicleta(request, pk):
    """Vista de detalle de una bicicleta."""
    bicicleta = get_object_or_404(Bicicleta, pk=pk, activo=True)
    return render(request, 'productos/detalle.html', {'bicicleta': bicicleta})
