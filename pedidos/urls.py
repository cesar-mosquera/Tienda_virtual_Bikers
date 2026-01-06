from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # Pedidos
    path('', views.lista_pedidos, name='lista'),
    path('crear/', views.crear_pedido, name='crear'),
    path('<int:pk>/', views.detalle_pedido, name='detalle'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado, name='cambiar_estado'),
    
    # Gestión de pedidos (Vendedor/Bodega)
    path('<int:pk>/tomar/', views.tomar_pedido, name='tomar'),
    path('<int:pk>/confirmar-vendedor/', views.confirmar_pedido_vendedor, name='confirmar_vendedor'),
    path('<int:pk>/despachar/', views.despachar_pedido, name='despachar'),
    
    # Carrito
    path('carrito/', views.ver_carrito, name='carrito'),
    path('carrito/agregar/<int:bicicleta_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/eliminar/<int:bicicleta_id>/', views.eliminar_del_carrito, name='eliminar_carrito'),
    path('carrito/actualizar/<int:bicicleta_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
]
