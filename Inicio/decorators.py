# Auth/decorators.py

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """
    Decorador que verifica si el usuario está autenticado y es de tipo 'ADMIN'.
    Si no lo es, redirige a la página de inicio con un mensaje de error.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.tipo_usuario == 'ADMIN':
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "No tienes permisos para acceder a esta sección.")
                return redirect('Propietarios:inicio')  # Asegúrate de que esta URL exista
        else:
            return redirect('Inicio:index')  # Redirigir a inicio si no está autenticado
    return _wrapped_view
