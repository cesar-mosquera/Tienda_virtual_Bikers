from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, Count
from .models import PQRS, Promocion
from productos.models import Bicicleta
from pedidos.models import Pedido


def admin_required(view_func):
    """Decorador para verificar que el usuario es administrador."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.es_admin:
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def dashboard(request):
    """Dashboard del administrador con métricas."""
    # Métricas de ventas
    total_pedidos = Pedido.objects.count()
    pedidos_entregados = Pedido.objects.filter(estado=Pedido.Estado.ENTREGADO).count()
    
    # Margen de ganancia promedio
    bicicletas = Bicicleta.objects.filter(activo=True)
    if bicicletas.exists():
        total_margen = sum(b.margen_ganancia for b in bicicletas) / bicicletas.count()
    else:
        total_margen = 0
    
    # PQRS pendientes
    pqrs_abiertos = PQRS.objects.filter(estado=PQRS.Estado.ABIERTO).count()
    
    # Promociones activas
    promociones_activas = Promocion.objects.filter(activa=True).count()
    
    # Productos con bajo stock
    bajo_stock = Bicicleta.objects.filter(stock__lt=3, activo=True).count()
    
    context = {
        'total_pedidos': total_pedidos,
        'pedidos_entregados': pedidos_entregados,
        'margen_promedio': total_margen,
        'pqrs_abiertos': pqrs_abiertos,
        'promociones_activas': promociones_activas,
        'bajo_stock': bajo_stock,
    }
    return render(request, 'administracion/dashboard.html', context)


@admin_required
def lista_pqrs(request):
    """Lista de PQRS."""
    pqrs = PQRS.objects.all()
    estado = request.GET.get('estado')
    if estado:
        pqrs = pqrs.filter(estado=estado)
    return render(request, 'administracion/lista_pqrs.html', {
        'pqrs': pqrs,
        'estados': PQRS.Estado.choices
    })


@admin_required
def detalle_pqrs(request, pk):
    """Detalle y resolución de PQRS."""
    pqrs = get_object_or_404(PQRS, pk=pk)
    
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        estado = request.POST.get('estado')
        
        pqrs.respuesta = respuesta
        pqrs.estado = estado
        if estado == PQRS.Estado.RESUELTO:
            pqrs.resuelto_por = request.user
            from django.utils import timezone
            pqrs.fecha_resolucion = timezone.now()
        pqrs.save()
        
        messages.success(request, 'PQRS actualizado exitosamente.')
        return redirect('administracion:lista_pqrs')
    
    return render(request, 'administracion/detalle_pqrs.html', {'pqrs': pqrs})


@admin_required
def lista_promociones(request):
    """Lista de promociones."""
    promociones = Promocion.objects.all()
    return render(request, 'administracion/lista_promociones.html', {'promociones': promociones})


@admin_required
def crear_promocion(request):
    """Crear nueva promoción."""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        descuento = request.POST.get('descuento')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        aplica_a_todas = request.POST.get('aplica_a_todas') == 'on'
        bicicletas_ids = request.POST.getlist('bicicletas')
        
        promocion = Promocion.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            descuento=descuento,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            aplica_a_todas=aplica_a_todas,
            creada_por=request.user
        )
        
        if not aplica_a_todas and bicicletas_ids:
            promocion.bicicletas.set(bicicletas_ids)
        
        messages.success(request, 'Promoción creada exitosamente.')
        return redirect('administracion:lista_promociones')
    
    bicicletas = Bicicleta.objects.filter(activo=True)
    return render(request, 'administracion/crear_promocion.html', {'bicicletas': bicicletas})
