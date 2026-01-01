from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from .models import IngresoStock, ProductoDanado, ConfirmacionDespacho
from pedidos.models import Pedido
from productos.models import Bicicleta


def bodeguero_required(view_func):
    """Decorador para verificar que el usuario es bodeguero."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.es_bodeguero or request.user.es_admin):
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@bodeguero_required
def panel_bodega(request):
    """Panel principal del bodeguero con métricas operativas."""
    hoy = timezone.now().date()
    
    # Solo pedidos CONFIRMADOS (listos para despachar)
    pedidos_para_despacho = Pedido.objects.filter(estado=Pedido.Estado.CONFIRMADO)
    ingresos_recientes = IngresoStock.objects.all()[:10]
    danos_pendientes = ProductoDanado.objects.filter(resuelto=False)
    
    # Métricas operativas
    metricas = {
        'para_despachar': pedidos_para_despacho.count(),
        'despachados_hoy': Pedido.objects.filter(
            estado=Pedido.Estado.DESPACHADO
        ).count(),
        'bajo_stock': Bicicleta.objects.filter(stock__lt=3, activo=True).count(),
        'sin_stock': Bicicleta.objects.filter(stock=0, activo=True).count(),
        'danos_pendientes': danos_pendientes.count(),
        'total_productos': Bicicleta.objects.filter(activo=True).count(),
    }
    
    # Productos con bajo stock
    productos_bajo_stock = Bicicleta.objects.filter(stock__lt=5, activo=True).order_by('stock')[:5]
    
    context = {
        'pedidos_para_despacho': pedidos_para_despacho,
        'ingresos_recientes': ingresos_recientes,
        'danos_pendientes': danos_pendientes,
        'metricas': metricas,
        'productos_bajo_stock': productos_bajo_stock,
    }
    return render(request, 'bodega/panel.html', context)


@bodeguero_required
def ingreso_stock(request):
    """Registrar ingreso de stock."""
    if request.method == 'POST':
        bicicleta_id = request.POST.get('bicicleta')
        cantidad = request.POST.get('cantidad')
        notas = request.POST.get('notas', '')
        
        bicicleta = get_object_or_404(Bicicleta, pk=bicicleta_id)
        IngresoStock.objects.create(
            bicicleta=bicicleta,
            cantidad=int(cantidad),
            confirmado_por=request.user,
            notas=notas
        )
        messages.success(request, f'Stock actualizado: +{cantidad} unidades de {bicicleta.modelo}')
        return redirect('bodega:panel')
    
    bicicletas = Bicicleta.objects.filter(activo=True)
    return render(request, 'bodega/ingreso_stock.html', {'bicicletas': bicicletas})


@bodeguero_required
def productos_danados(request):
    """Lista de productos dañados."""
    danos = ProductoDanado.objects.all()
    return render(request, 'bodega/productos_danados.html', {'danos': danos})


@bodeguero_required
def registrar_dano(request):
    """Registrar un producto dañado."""
    if request.method == 'POST':
        bicicleta_id = request.POST.get('bicicleta')
        motivo_tipo = request.POST.get('motivo_tipo')
        motivo_descripcion = request.POST.get('motivo_descripcion')
        cantidad = request.POST.get('cantidad', 1)
        foto = request.FILES.get('foto_evidencia')
        
        bicicleta = get_object_or_404(Bicicleta, pk=bicicleta_id)
        ProductoDanado.objects.create(
            bicicleta=bicicleta,
            motivo_tipo=motivo_tipo,
            motivo_descripcion=motivo_descripcion,
            cantidad_afectada=int(cantidad),
            foto_evidencia=foto,
            reportado_por=request.user
        )
        messages.success(request, 'Daño registrado exitosamente.')
        return redirect('bodega:productos_danados')
    
    bicicletas = Bicicleta.objects.filter(activo=True)
    motivos = ProductoDanado.Motivo.choices
    return render(request, 'bodega/registrar_dano.html', {
        'bicicletas': bicicletas,
        'motivos': motivos
    })


@bodeguero_required
def confirmar_despacho(request, pedido_id):
    """Confirmar despacho de un pedido."""
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    
    if request.method == 'POST':
        notas = request.POST.get('notas', '')
        
        # Crear confirmación de despacho
        ConfirmacionDespacho.objects.create(
            pedido=pedido,
            confirmado_por=request.user,
            notas=notas
        )
        
        # Cambiar estado del pedido
        pedido.cambiar_estado(Pedido.Estado.DESPACHADO, request.user)
        messages.success(request, f'Pedido #{pedido.pk} despachado exitosamente.')
        return redirect('bodega:panel')
    
    return render(request, 'bodega/confirmar_despacho.html', {'pedido': pedido})
