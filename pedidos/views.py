from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Pedido, DetallePedido, HistorialEstadoPedido
from .carrito import Carrito
from productos.models import Bicicleta


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
    user = request.user
    
    # Clientes solo pueden ver sus propios pedidos
    if user.es_cliente and pedido.cliente != user:
        messages.error(request, 'No tienes permiso para ver este pedido.')
        return redirect('pedidos:lista')
    
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


# ============================================================
# VISTAS DEL CARRITO
# ============================================================

@login_required
def ver_carrito(request):
    """Muestra el carrito de compras."""
    carrito = Carrito(request)
    return render(request, 'pedidos/carrito.html', {
        'carrito_items': carrito.get_items(),
        'carrito_total': carrito.get_total()
    })


@login_required
@require_POST
def agregar_al_carrito(request, bicicleta_id):
    """Agrega una bicicleta al carrito."""
    bicicleta = get_object_or_404(Bicicleta, id=bicicleta_id)
    carrito = Carrito(request)
    
    cantidad = int(request.POST.get('cantidad', 1))
    exito, mensaje = carrito.agregar(bicicleta, cantidad)
    
    if exito:
        messages.success(request, mensaje)
    else:
        messages.error(request, mensaje)
    
    # Redirigir a donde vino el usuario
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


@login_required
@require_POST
def eliminar_del_carrito(request, bicicleta_id):
    """Elimina una bicicleta del carrito."""
    carrito = Carrito(request)
    carrito.eliminar(bicicleta_id)
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('pedidos:carrito')


@login_required
@require_POST
def actualizar_carrito(request, bicicleta_id):
    """Actualiza la cantidad de una bicicleta en el carrito."""
    carrito = Carrito(request)
    cantidad = int(request.POST.get('cantidad', 1))
    
    exito, mensaje = carrito.actualizar_cantidad(bicicleta_id, cantidad)
    
    if exito:
        messages.success(request, mensaje)
    else:
        messages.error(request, mensaje)
    
    return redirect('pedidos:carrito')


@login_required
def checkout(request):
    """Vista de checkout para confirmar el pedido."""
    carrito = Carrito(request)
    
    # Verificar que hay items en el carrito
    if len(carrito) == 0:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('pedidos:carrito')
    
    if request.method == 'POST':
        direccion = request.POST.get('direccion', '').strip()
        notas = request.POST.get('notas', '').strip()
        
        if not direccion:
            messages.error(request, 'Por favor ingresa una dirección de envío.')
            return render(request, 'pedidos/checkout.html', {
                'carrito_items': carrito.get_items(),
                'carrito_total': carrito.get_total()
            })
        
        # Verificar stock antes de crear el pedido
        items = carrito.get_items()
        for item in items:
            bicicleta = item['bicicleta']
            if item['cantidad'] > bicicleta.stock:
                messages.error(
                    request,
                    f'No hay suficiente stock de {bicicleta.marca} {bicicleta.modelo}. '
                    f'Disponible: {bicicleta.stock}'
                )
                return redirect('pedidos:carrito')
        
        # Crear el pedido
        pedido = Pedido.objects.create(
            cliente=request.user,
            direccion_envio=direccion,
            notas=notas,
            estado=Pedido.Estado.PENDIENTE,
            total=carrito.get_total()
        )
        
        # Crear los detalles del pedido y descontar stock
        for item in items:
            bicicleta = item['bicicleta']
            DetallePedido.objects.create(
                pedido=pedido,
                bicicleta=bicicleta,
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            # Descontar stock
            bicicleta.stock -= item['cantidad']
            bicicleta.save()
        
        # Limpiar el carrito
        carrito.limpiar()
        
        messages.success(
            request,
            f'¡Pedido #{pedido.pk} creado exitosamente! '
            f'Te notificaremos cuando sea despachado.'
        )
        return redirect('pedidos:detalle', pk=pedido.pk)
    
    return render(request, 'pedidos/checkout.html', {
        'carrito_items': carrito.get_items(),
        'carrito_total': carrito.get_total(),
        'direccion_predeterminada': request.user.direccion or ''
    })
