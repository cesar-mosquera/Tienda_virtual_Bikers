"""
URL configuration for aura_bikers project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('productos/', include('productos.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('bodega/', include('bodega.urls')),
    path('administracion/', include('administracion.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Personalización del admin
admin.site.site_header = "Aura Bikers - Panel de Administración"
admin.site.site_title = "Aura Bikers Admin"
admin.site.index_title = "Gestión de la Tienda"
