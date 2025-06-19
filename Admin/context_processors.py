# admin/context_processors.py

from django.urls import reverse

def menu_context(request):
    if not request.user.is_authenticated:
        return {}

    menu = {
        "Centros": [
            {"name": "Sedes", "icon": "fa-map-marker-alt", "url": reverse('Admin:sedes')},
            {"name": "Almacenes", "icon": "fa-warehouse", "url": reverse('Admin:almacenes')},
        ],
        "Materiales": [
            {"name": "Materiales (ROH)", "icon": "fa-box", "url": reverse('Admin:materiales')},
            {"name": "BOM (FERT)", "icon": "fa-project-diagram", "url": reverse('Admin:bom')},
        ],
        "Planificación": [
            {"name": "Planes de Producción", "icon": "fa-tasks", "url": reverse('Admin:planificacion')},
            {"name": "SOLPED", "icon": "fa-file-signature", "url": reverse('Admin:solped')},
        ],
        "Aprobación": [
            {"name": "Revisar SOLPED", "icon": "fa-check-circle", "url": reverse('Admin:aprobacion')},
        ],
        "Compras": [
            {"name": "Proveedores", "icon": "fa-handshake", "url": reverse('Admin:proveedores')},
            {"name": "Órdenes de Compra", "icon": "fa-shopping-cart", "url": reverse('Admin:ordenes_compra')},
        ],
        "Almacén": [
            {"name": "Entradas de Materiales", "icon": "fa-truck-loading", "url": reverse('Admin:entradas')},
            {"name": "Movimientos de Stock", "icon": "fa-exchange-alt", "url": reverse('Admin:movimientos')},
        ],
    }

    return {"menu_links": menu}


