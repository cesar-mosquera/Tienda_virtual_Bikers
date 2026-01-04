"""
Clase Carrito para manejar el carrito de compras usando sesiones.
"""
from decimal import Decimal
from productos.models import Bicicleta


class Carrito:
    """
    Carrito de compras almacenado en la sesión del usuario.
    """
    
    def __init__(self, request):
        """Inicializa el carrito desde la sesión."""
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito
    
    def agregar(self, bicicleta, cantidad=1):
        """
        Agrega una bicicleta al carrito o actualiza su cantidad.
        Retorna (exito, mensaje).
        """
        bicicleta_id = str(bicicleta.id)
        
        # Validar disponibilidad
        if not bicicleta.disponible:
            return False, "Este producto está agotado."
        
        # Calcular cantidad total (actual + nueva)
        cantidad_actual = self.carrito.get(bicicleta_id, {}).get('cantidad', 0)
        cantidad_total = cantidad_actual + cantidad
        
        # Validar stock suficiente
        if cantidad_total > bicicleta.stock:
            return False, f"Solo hay {bicicleta.stock} unidades disponibles."
        
        if bicicleta_id not in self.carrito:
            self.carrito[bicicleta_id] = {
                'cantidad': 0,
                'precio': str(bicicleta.precio)
            }
        
        self.carrito[bicicleta_id]['cantidad'] = cantidad_total
        self.guardar()
        return True, "Producto agregado al carrito."
    
    def eliminar(self, bicicleta_id):
        """Elimina una bicicleta del carrito."""
        bicicleta_id = str(bicicleta_id)
        if bicicleta_id in self.carrito:
            del self.carrito[bicicleta_id]
            self.guardar()
    
    def actualizar_cantidad(self, bicicleta_id, cantidad):
        """
        Actualiza la cantidad de una bicicleta.
        Retorna (exito, mensaje).
        """
        bicicleta_id = str(bicicleta_id)
        
        if bicicleta_id not in self.carrito:
            return False, "Producto no encontrado en el carrito."
        
        if cantidad <= 0:
            self.eliminar(bicicleta_id)
            return True, "Producto eliminado del carrito."
        
        # Validar stock
        try:
            bicicleta = Bicicleta.objects.get(id=bicicleta_id)
            if cantidad > bicicleta.stock:
                return False, f"Solo hay {bicicleta.stock} unidades disponibles."
        except Bicicleta.DoesNotExist:
            self.eliminar(bicicleta_id)
            return False, "Producto no encontrado."
        
        self.carrito[bicicleta_id]['cantidad'] = cantidad
        self.guardar()
        return True, "Cantidad actualizada."
    
    def limpiar(self):
        """Vacía el carrito."""
        del self.session['carrito']
        self.guardar()
    
    def guardar(self):
        """Marca la sesión como modificada para que se guarde."""
        self.session.modified = True
    
    def get_items(self):
        """
        Retorna los items del carrito con datos completos de bicicleta.
        """
        bicicleta_ids = self.carrito.keys()
        bicicletas = Bicicleta.objects.filter(id__in=bicicleta_ids)
        
        items = []
        for bicicleta in bicicletas:
            item = self.carrito[str(bicicleta.id)]
            items.append({
                'bicicleta': bicicleta,
                'cantidad': item['cantidad'],
                'precio': Decimal(item['precio']),
                'subtotal': Decimal(item['precio']) * item['cantidad']
            })
        return items
    
    def get_total(self):
        """Calcula el total del carrito."""
        return sum(
            Decimal(item['precio']) * item['cantidad']
            for item in self.carrito.values()
        )
    
    def __len__(self):
        """Retorna el número total de items en el carrito."""
        return sum(item['cantidad'] for item in self.carrito.values())
    
    def __iter__(self):
        """Itera sobre los items del carrito."""
        return iter(self.get_items())
