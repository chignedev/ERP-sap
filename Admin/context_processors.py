# admin/context_processors.py

from django.urls import reverse

def menu_context(request):
    if not request.user.is_authenticated:
        return {}

    menu = [
        {"name": "Dashboard", "icon": "fa-chart-line", "url": reverse('Admin:inicio')},
    
    ]
    return {"menu_links": menu}
