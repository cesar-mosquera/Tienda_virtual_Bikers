from django.urls import path
from . import views

app_name = 'bodega'

urlpatterns = [
    path('', views.panel_bodega, name='panel'),
    path('ingreso-stock/', views.ingreso_stock, name='ingreso_stock'),
    path('productos-danados/', views.productos_danados, name='productos_danados'),
    path('registrar-dano/', views.registrar_dano, name='registrar_dano'),
    path('confirmar-despacho/<int:pedido_id>/', views.confirmar_despacho, name='confirmar_despacho'),
]
