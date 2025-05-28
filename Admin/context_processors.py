# admin/context_processors.py

from django.urls import reverse

def menu_context(request):
    if not request.user.is_authenticated:
        return {}

    menu = [
        {"name": "Dashboard", "icon": "fa-tachometer-alt", "url": reverse('Admin:inicio')},
        {"name": "Centros", "icon": "fa-building", "url": reverse('Admin:centros')},
        {"name": "Materiales", "icon": "fa-boxes", "url": reverse('Admin:materiales')},
    
    ]
    return {"menu_links": menu}
