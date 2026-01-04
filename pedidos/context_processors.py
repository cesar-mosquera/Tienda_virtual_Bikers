"""
Context processors para la aplicación pedidos.
"""
from .carrito import Carrito


def carrito(request):
    """
    Context processor que hace el carrito disponible en todos los templates.
    """
    return {'carrito': Carrito(request)}
