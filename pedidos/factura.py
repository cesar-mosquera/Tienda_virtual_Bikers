from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


def generar_factura_pdf(pedido):
    """Genera un PDF de factura para el pedido."""
    template = get_template('pedidos/factura_pdf.html')
    
    context = {
        'pedido': pedido,
        'empresa': {
            'nombre': 'Aura Bikers',
            'ruc': '1712345678001',
            'direccion': 'Av. Solanda y José Argudo, Quito - Ecuador',
            'telefono': '(+593) 99 123 4567',
            'email': 'ventas@aurabikers.com',
        }
    }
    
    html = template.render(context)
    
    # Crear PDF
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)
    
    if pdf.err:
        return None
    
    return result.getvalue()


def descargar_factura_response(pedido, descargar=False):
    """Retorna HttpResponse con el PDF para ver o descargar."""
    pdf_content = generar_factura_pdf(pedido)
    
    if pdf_content is None:
        return None
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    
    if descargar:
        response['Content-Disposition'] = f'attachment; filename="Factura_Pedido_{pedido.pk}.pdf"'
    else:
        response['Content-Disposition'] = f'inline; filename="Factura_Pedido_{pedido.pk}.pdf"'
    
    return response
