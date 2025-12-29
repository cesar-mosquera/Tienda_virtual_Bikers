from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pqrs/', views.lista_pqrs, name='lista_pqrs'),
    path('pqrs/<int:pk>/', views.detalle_pqrs, name='detalle_pqrs'),
    path('promociones/', views.lista_promociones, name='lista_promociones'),
    path('promociones/crear/', views.crear_promocion, name='crear_promocion'),
]
