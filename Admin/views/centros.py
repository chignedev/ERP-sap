from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Inicio.models import Centro
import json

def centros(request):
    context = {
        'centros': Centro.objects.all()
    }
    return render(request, 'admin/centros.html', context)

@csrf_exempt
def guardar_centro(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        codigo = data.get('codigo')
        nombre = data.get('nombre')

        if not codigo or not nombre:
            return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios'})

        if id:
            centro = Centro.objects.get(id=id)
            centro.codigo = codigo
            centro.nombre = nombre
            centro.save()
        else:
            if Centro.objects.filter(codigo=codigo).exists():
                return JsonResponse({'ok': False, 'error': 'Código ya registrado'})
            Centro.objects.create(codigo=codigo, nombre=nombre)

        return JsonResponse({'ok': True})

@csrf_exempt
def eliminar_centro(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        try:
            Centro.objects.get(id=id).delete()
            return JsonResponse({'ok': True})
        except:
            return JsonResponse({'ok': False, 'error': 'No se pudo eliminar'})
