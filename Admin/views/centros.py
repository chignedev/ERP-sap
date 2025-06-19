from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Inicio.models import Sede, Almacen
import json

# ================================
# 📌 CRUD de Sedes
# ================================

def sedes(request):
    context = {
        'sedes': Sede.objects.all()
    }
    return render(request, 'admin/sedes.html', context)

@csrf_exempt
def guardar_sede(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        nombre = data.get('nombre')
        direccion = data.get('direccion')
        ciudad = data.get('ciudad')
        pais = data.get('pais')

        # Validación básica
        if not nombre or not direccion or not ciudad or not pais:
            return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios'})

        if id:
            sede = get_object_or_404(Sede, id=id)
            sede.nombre = nombre
            sede.direccion = direccion
            sede.ciudad = ciudad
            sede.pais = pais
            sede.save()
        else:
            Sede.objects.create(
                nombre=nombre,
                direccion=direccion,
                ciudad=ciudad,
                pais=pais
            )

        return JsonResponse({'ok': True})


@csrf_exempt
def eliminar_sede(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        try:
            sede = get_object_or_404(Sede, id=id)
            sede.delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})


# ================================
# 📌 CRUD de Almacenes
# ================================

def almacenes(request):
    context = {
        'almacenes': Almacen.objects.select_related('sede').all(),
        'sedes': Sede.objects.all()  # Para permitir elegir la sede al crear o editar
    }
    return render(request, 'admin/almacenes.html', context)

@csrf_exempt
def guardar_almacen(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        nombre = data.get('nombre')
        descripcion = data.get('descripcion', '')
        sede_id = data.get('sede_id')

        if not nombre or not sede_id:
            return JsonResponse({'ok': False, 'error': 'Nombre y Sede son obligatorios'})

        sede = get_object_or_404(Sede, id=sede_id)

        if id:
            almacen = get_object_or_404(Almacen, id=id)
            almacen.nombre = nombre
            almacen.descripcion = descripcion
            almacen.sede = sede
            almacen.save()
        else:
            Almacen.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                sede=sede
            )

        return JsonResponse({'ok': True})


@csrf_exempt
def eliminar_almacen(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        try:
            almacen = get_object_or_404(Almacen, id=id)
            almacen.delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})
