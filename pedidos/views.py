from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pedido, DetallePedido, HistorialEstadoPedido


@login_required
def lista_pedidos(request):
    """Lista de pedidos según el rol del usuario."""
    user = request.user
    
    if user.es_cliente:
        pedidos = Pedido.objects.filter(cliente=user)
    elif user.es_vendedor:
        pedidos = Pedido.objects.filter(vendedor=user)
    elif user.es_bodeguero:
        pedidos = Pedido.objects.filter(estado=Pedido.Estado.PENDIENTE)
    else:  # Admin
        pedidos = Pedido.objects.all()
    
    return render(request, 'pedidos/lista.html', {'pedidos': pedidos})


@login_required
def crear_pedido(request):
    """Crear nuevo pedido."""
    # TODO: Implementar lógica completa de creación de pedido
    return render(request, 'pedidos/crear.html')


@login_required
def detalle_pedido(request, pk):
    """Ver detalle de un pedido con su historial."""
    pedido = get_object_or_404(Pedido, pk=pk)
    historial = pedido.historial_estados.all()
    return render(request, 'pedidos/detalle.html', {
        'pedido': pedido,
        'historial': historial
    })


@login_required
def cambiar_estado(request, pk):
    """Cambiar el estado de un pedido."""
    pedido = get_object_or_404(Pedido, pk=pk)
    user = request.user
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        
        # Validar permisos de cambio de estado
        puede_cambiar = False
        
        if user.es_bodeguero and nuevo_estado == Pedido.Estado.DESPACHADO:
            puede_cambiar = True
        elif user.es_vendedor and nuevo_estado in [Pedido.Estado.EN_CAMINO, Pedido.Estado.ENTREGADO]:
            puede_cambiar = True
        elif user.es_admin:
            puede_cambiar = True
        
        if puede_cambiar:
            pedido.cambiar_estado(nuevo_estado, user)
            messages.success(request, f'Estado cambiado a {pedido.get_estado_display()}')
        else:
            messages.error(request, 'No tienes permiso para realizar este cambio.')
        
        return redirect('pedidos:detalle', pk=pk)
    
    return render(request, 'pedidos/cambiar_estado.html', {'pedido': pedido})
