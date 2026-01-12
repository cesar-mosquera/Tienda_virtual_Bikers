from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum
from .models import Pedido, DetallePedido, HistorialEstadoPedido
from .carrito import Carrito
from productos.models import Bicicleta


@login_required
def lista_pedidos(request):
    """Lista de pedidos según el rol del usuario con métricas."""
    user = request.user
    context = {}
    
    if user.es_cliente:
        # Cliente: solo sus pedidos con resumen por estado
        pedidos = Pedido.objects.filter(cliente=user)
        
        # Métricas del cliente
        context['metricas'] = {
            'pendientes': pedidos.filter(estado=Pedido.Estado.PENDIENTE).count(),
            'en_proceso': pedidos.filter(estado__in=[
                Pedido.Estado.CONFIRMADO, 
                Pedido.Estado.DESPACHADO, 
                Pedido.Estado.EN_CAMINO
            ]).count(),
            'entregados': pedidos.filter(estado=Pedido.Estado.ENTREGADO).count(),
            'total_compras': pedidos.filter(estado=Pedido.Estado.ENTREGADO).aggregate(
                total=Sum('total')
            )['total'] or 0,
        }
        
    elif user.es_vendedor:
        # Vendedor: pedidos pendientes sin asignar + sus pedidos asignados
        pedidos_pendientes = Pedido.objects.filter(
            estado=Pedido.Estado.PENDIENTE,
            vendedor__isnull=True
        )
        pedidos = Pedido.objects.filter(vendedor=user).exclude(
            estado__in=[Pedido.Estado.ENTREGADO, Pedido.Estado.CANCELADO]
        )
        context['pedidos_pendientes'] = pedidos_pendientes
        
        # Métricas del vendedor
        mis_pedidos = Pedido.objects.filter(vendedor=user)
        context['metricas'] = {
            'sin_asignar': pedidos_pendientes.count(),
            'pendientes': mis_pedidos.filter(estado=Pedido.Estado.PENDIENTE).count(),
            'confirmados': mis_pedidos.filter(estado=Pedido.Estado.CONFIRMADO).count(),
            'despachados': mis_pedidos.filter(estado=Pedido.Estado.DESPACHADO).count(),
            'en_camino': mis_pedidos.filter(estado=Pedido.Estado.EN_CAMINO).count(),
            'entregados_total': mis_pedidos.filter(estado=Pedido.Estado.ENTREGADO).count(),
        }
        
    elif user.es_bodeguero:
        # Bodeguero: solo pedidos CONFIRMADOS (listos para despachar)
        pedidos = Pedido.objects.filter(estado=Pedido.Estado.CONFIRMADO)
        
        # Métricas del bodeguero
        context['metricas'] = {
            'para_despachar': pedidos.count(),
            'despachados_hoy': Pedido.objects.filter(
                estado=Pedido.Estado.DESPACHADO,
                fecha_actualizacion__date=__import__('django.utils.timezone', fromlist=['now']).now().date()
            ).count(),
            'bajo_stock': Bicicleta.objects.filter(stock__lt=3, activo=True).count(),
        }
        
    else:  # Admin
        pedidos = Pedido.objects.all()
        
        # Métricas globales del admin
        context['metricas'] = {
            'total_pedidos': pedidos.count(),
            'pendientes': pedidos.filter(estado=Pedido.Estado.PENDIENTE).count(),
            'confirmados': pedidos.filter(estado=Pedido.Estado.CONFIRMADO).count(),
            'despachados': pedidos.filter(estado=Pedido.Estado.DESPACHADO).count(),
            'en_camino': pedidos.filter(estado=Pedido.Estado.EN_CAMINO).count(),
            'entregados': pedidos.filter(estado=Pedido.Estado.ENTREGADO).count(),
            'ingresos_totales': pedidos.filter(estado=Pedido.Estado.ENTREGADO).aggregate(
                total=Sum('total')
            )['total'] or 0,
        }
    
    context['pedidos'] = pedidos
    return render(request, 'pedidos/lista.html', context)


@login_required
def crear_pedido(request):
    """Crear nuevo pedido."""
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
        
        if user.es_vendedor and pedido.vendedor == user:
            # Vendedor asignado puede: CONFIRMADO -> EN_CAMINO -> ENTREGADO
            if nuevo_estado in [Pedido.Estado.CONFIRMADO, Pedido.Estado.EN_CAMINO, Pedido.Estado.ENTREGADO]:
                puede_cambiar = True
        elif user.es_bodeguero and nuevo_estado == Pedido.Estado.DESPACHADO:
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
# VISTAS DE GESTIÓN DE PEDIDOS (VENDEDOR)
# ============================================================

@login_required
@require_POST
def tomar_pedido(request, pk):
    """Vendedor toma un pedido pendiente sin asignar."""
    pedido = get_object_or_404(Pedido, pk=pk)
    user = request.user
    
    if not (user.es_vendedor or user.es_admin):
        messages.error(request, 'No tienes permiso para tomar pedidos.')
        return redirect('pedidos:lista')
    
    # Verificar que el pedido está pendiente y sin vendedor
    if pedido.estado != Pedido.Estado.PENDIENTE:
        messages.error(request, 'Este pedido ya no está pendiente.')
        return redirect('pedidos:lista')
    
    if pedido.vendedor is not None:
        messages.error(request, 'Este pedido ya fue tomado por otro vendedor.')
        return redirect('pedidos:lista')
    
    # Asignar vendedor
    pedido.vendedor = user
    pedido.save(update_fields=['vendedor'])
    
    messages.success(request, f'Has tomado el pedido #{pedido.pk}. Ahora puedes confirmarlo.')
    return redirect('pedidos:detalle', pk=pk)


@login_required
@require_POST
def confirmar_pedido_vendedor(request, pk):
    """Vendedor confirma el pedido para que pase a bodega."""
    pedido = get_object_or_404(Pedido, pk=pk)
    user = request.user
    
    # Verificar permisos
    if not (user.es_admin or (user.es_vendedor and pedido.vendedor == user)):
        messages.error(request, 'No tienes permiso para confirmar este pedido.')
        return redirect('pedidos:detalle', pk=pk)
    
    if pedido.estado != Pedido.Estado.PENDIENTE:
        messages.error(request, 'Solo se pueden confirmar pedidos pendientes.')
        return redirect('pedidos:detalle', pk=pk)
    
    # Cambiar estado a CONFIRMADO
    pedido.cambiar_estado(Pedido.Estado.CONFIRMADO, user)
    messages.success(request, f'Pedido #{pedido.pk} confirmado. Ahora está listo para bodega.')
    return redirect('pedidos:detalle', pk=pk)


@login_required
@require_POST
def despachar_pedido(request, pk):
    """Bodeguero despacha el pedido y descuenta stock."""
    pedido = get_object_or_404(Pedido, pk=pk)
    user = request.user
    
    # Verificar permisos
    if not (user.es_bodeguero or user.es_admin):
        messages.error(request, 'No tienes permiso para despachar pedidos.')
        return redirect('pedidos:detalle', pk=pk)
    
    if pedido.estado != Pedido.Estado.CONFIRMADO:
        messages.error(request, 'Solo se pueden despachar pedidos confirmados.')
        return redirect('pedidos:detalle', pk=pk)
    
    # Verificar y descontar stock
    for detalle in pedido.detalles.all():
        if detalle.cantidad > detalle.bicicleta.stock:
            messages.error(
                request,
                f'Stock insuficiente para {detalle.bicicleta.marca} {detalle.bicicleta.modelo}. '
                f'Disponible: {detalle.bicicleta.stock}, Requerido: {detalle.cantidad}'
            )
            return redirect('pedidos:detalle', pk=pk)
    
    # Descontar stock
    for detalle in pedido.detalles.all():
        detalle.bicicleta.stock -= detalle.cantidad
        detalle.bicicleta.save()
    
    # Cambiar estado a DESPACHADO
    pedido.cambiar_estado(Pedido.Estado.DESPACHADO, user)
    messages.success(request, f'Pedido #{pedido.pk} despachado. Stock descontado.')
    return redirect('pedidos:detalle', pk=pk)


@login_required
def cancelar_pedido(request, pk):
    """Cancelar un pedido con reglas de negocio."""
    pedido = get_object_or_404(Pedido, pk=pk)
    user = request.user
    
    # No se puede cancelar un pedido ya entregado o cancelado
    if pedido.estado in [Pedido.Estado.ENTREGADO, Pedido.Estado.CANCELADO]:
        messages.error(request, 'Este pedido no puede ser cancelado.')
        return redirect('pedidos:detalle', pk=pk)
    
    # Verificar permisos según rol
    puede_cancelar = False
    requiere_motivo = True
    
    if user.es_admin:
        # Admin puede cancelar cualquier pedido (excepto entregado)
        puede_cancelar = True
    elif user.es_vendedor and (pedido.vendedor == user or pedido.vendedor is None):
        # Vendedor puede cancelar PENDIENTE o CONFIRMADO
        if pedido.estado in [Pedido.Estado.PENDIENTE, Pedido.Estado.CONFIRMADO]:
            puede_cancelar = True
    elif user.es_cliente and pedido.cliente == user:
        # Cliente solo puede cancelar PENDIENTE
        if pedido.estado == Pedido.Estado.PENDIENTE:
            puede_cancelar = True
            requiere_motivo = False
    
    if not puede_cancelar:
        messages.error(request, 'No tienes permiso para cancelar este pedido.')
        return redirect('pedidos:detalle', pk=pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        
        if requiere_motivo and not motivo:
            messages.error(request, 'Debes indicar un motivo para la cancelación.')
            return render(request, 'pedidos/cancelar.html', {
                'pedido': pedido,
                'requiere_motivo': requiere_motivo
            })
        
        # Si el pedido ya fue despachado, restaurar stock
        if pedido.estado == Pedido.Estado.DESPACHADO:
            for detalle in pedido.detalles.all():
                detalle.bicicleta.stock += detalle.cantidad
                detalle.bicicleta.save()
            messages.info(request, 'Stock restaurado.')
        
        # Cambiar estado a CANCELADO
        notas_cancelacion = f"Cancelado por {user.username}"
        if motivo:
            notas_cancelacion += f". Motivo: {motivo}"
        
        pedido.notas = notas_cancelacion if not pedido.notas else f"{pedido.notas}\n{notas_cancelacion}"
        pedido.save(update_fields=['notas'])
        pedido.cambiar_estado(Pedido.Estado.CANCELADO, user)
        
        messages.success(request, f'Pedido #{pedido.pk} cancelado exitosamente.')
        return redirect('pedidos:lista')
    
    return render(request, 'pedidos/cancelar.html', {
        'pedido': pedido,
        'requiere_motivo': requiere_motivo
    })


@login_required
def descargar_factura(request, pk):
    """Ver o descargar factura PDF del pedido."""
    from .factura import descargar_factura_response
    
    pedido = get_object_or_404(Pedido, pk=pk)
    user = request.user
    
    # Verificar permisos
    puede_ver = False
    if user.es_admin:
        puede_ver = True
    elif user.es_vendedor and pedido.vendedor == user:
        puede_ver = True
    elif user.es_cliente and pedido.cliente == user:
        puede_ver = True
    
    if not puede_ver:
        messages.error(request, 'No tienes permiso para ver esta factura.')
        return redirect('pedidos:lista')
    
    # No se puede generar factura de pedidos cancelados
    if pedido.estado == Pedido.Estado.CANCELADO:
        messages.warning(request, 'No se puede generar factura de un pedido cancelado.')
        return redirect('pedidos:detalle', pk=pk)
    
    # Verificar si es descarga o visualización
    descargar = request.GET.get('descargar', '0') == '1'
    
    response = descargar_factura_response(pedido, descargar=descargar)
    if response is None:
        messages.error(request, 'Error al generar la factura.')
        return redirect('pedidos:detalle', pk=pk)
    
    return response


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
        
        # Crear el pedido (sin descontar stock - se hace al despachar)
        pedido = Pedido.objects.create(
            cliente=request.user,
            direccion_envio=direccion,
            notas=notas,
            estado=Pedido.Estado.PENDIENTE,
            total=carrito.get_total()
        )
        
        # Crear los detalles del pedido (sin descontar stock)
        for item in items:
            bicicleta = item['bicicleta']
            DetallePedido.objects.create(
                pedido=pedido,
                bicicleta=bicicleta,
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
        
        # Limpiar el carrito
        carrito.limpiar()
        
        messages.success(
            request,
            f'¡Pedido #{pedido.pk} creado exitosamente! '
            f'Un vendedor lo tomará pronto.'
        )
        return redirect('pedidos:detalle', pk=pedido.pk)
    
    return render(request, 'pedidos/checkout.html', {
        'carrito_items': carrito.get_items(),
        'carrito_total': carrito.get_total(),
        'direccion_predeterminada': request.user.direccion or ''
    })
