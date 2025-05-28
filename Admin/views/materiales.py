from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Inicio.models import Material, Centro, ComponenteMaterial
from django.db.models import Q
import json


def materiales(request):
    context = {
        'materiales': Material.objects.select_related('centro').all(),
        'centros': Centro.objects.all(),
        'materiales_disponibles': Material.objects.exclude(tipo='SERV')  # Para seleccionar componentes
    }
    return render(request, 'admin/materiales.html', context)


def generar_codigo_material():
    ultimo = Material.objects.order_by('-id').first()
    numero = ultimo.id + 1 if ultimo else 1
    return f"MAT{str(numero).zfill(4)}"


@csrf_exempt
def guardar_material(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        nombre = data.get('nombre')
        tipo = data.get('tipo')
        unidad_medida = data.get('unidad_medida')
        precio = data.get('precio')
        centro_id = data.get('centro')

        if not all([nombre, tipo, unidad_medida, precio, centro_id]):
            return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios'})

        try:
            centro = Centro.objects.get(id=centro_id)
        except Centro.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Centro inválido'})

        if id:
            try:
                material = Material.objects.get(id=id)
                material.nombre = nombre
                material.tipo = tipo
                material.unidad_medida = unidad_medida
                material.precio = precio
                material.centro = centro
                material.save()
            except Material.DoesNotExist:
                return JsonResponse({'ok': False, 'error': 'Material no encontrado'})
        else:
            codigo = generar_codigo_material()
            while Material.objects.filter(codigo=codigo).exists():
                codigo = generar_codigo_material()

            Material.objects.create(
                codigo=codigo,
                nombre=nombre,
                tipo=tipo,
                unidad_medida=unidad_medida,
                precio=precio,
                centro=centro
            )

        return JsonResponse({'ok': True})


@csrf_exempt
def eliminar_material(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        try:
            Material.objects.get(id=id).delete()
            return JsonResponse({'ok': True})
        except Material.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Material no encontrado'})


# 🎯 Obtener los componentes de un material (tipo FERT o HALB)
def listar_componentes(request, material_id):
    componentes = ComponenteMaterial.objects.filter(material_padre_id=material_id).select_related('componente')
    data = [{
        'id': c.id,
        'codigo': c.componente.codigo,
        'nombre': c.componente.nombre,
        'cantidad': float(c.cantidad)
    } for c in componentes]
    return JsonResponse({'ok': True, 'componentes': data})


# 🧩 Añadir o editar componente de material
@csrf_exempt
def guardar_componente(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        padre_id = data.get('padre_id')
        componente_id = data.get('componente_id')
        cantidad = data.get('cantidad')

        if not all([padre_id, componente_id, cantidad]):
            return JsonResponse({'ok': False, 'error': 'Datos incompletos'})

        if padre_id == componente_id:
            return JsonResponse({'ok': False, 'error': 'Un material no puede componerse de sí mismo'})

        try:
            padre = Material.objects.get(id=padre_id)
            componente = Material.objects.get(id=componente_id)

            # Evitar duplicados
            existente = ComponenteMaterial.objects.filter(
                material_padre=padre, componente=componente
            ).first()

            if existente:
                existente.cantidad = cantidad
                existente.save()
            else:
                ComponenteMaterial.objects.create(
                    material_padre=padre,
                    componente=componente,
                    cantidad=cantidad
                )

            return JsonResponse({'ok': True})
        except Material.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Material no encontrado'})


# ❌ Eliminar componente
@csrf_exempt
def eliminar_componente(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        componente_id = data.get('id')
        try:
            ComponenteMaterial.objects.get(id=componente_id).delete()
            return JsonResponse({'ok': True})
        except ComponenteMaterial.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Componente no encontrado'})

from Inicio.models import ComponenteMaterial

def ver_componentes(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    componentes = ComponenteMaterial.objects.filter(material_padre=material).select_related('componente')

    # Excluye al material padre y los que empiezan con tipo 'FERT'
    materiales = Material.objects.exclude(id=material.id).exclude(tipo__startswith='FERT')

    data = [
        {
            'id': c.id,
            'componente_id': c.componente.id,
            'componente_nombre': c.componente.nombre,
            'unidad': c.componente.unidad_medida,
            'cantidad': float(c.cantidad)
        }
        for c in componentes
    ]

    opciones = [
        {'id': m.id, 'nombre': m.nombre, 'unidad': m.unidad_medida}
        for m in materiales
    ]

    return JsonResponse({'ok': True, 'componentes': data, 'materiales': opciones})


@csrf_exempt
def guardar_componente(request):
    data = json.loads(request.body)
    id = data.get('id')
    padre = Material.objects.get(id=data.get('material_padre'))
    comp = Material.objects.get(id=data.get('componente'))
    cantidad = data.get('cantidad')

    if id:
        comp_mat = ComponenteMaterial.objects.get(id=id)
        comp_mat.componente = comp
        comp_mat.cantidad = cantidad
        comp_mat.save()
    else:
        ComponenteMaterial.objects.create(material_padre=padre, componente=comp, cantidad=cantidad)

    return JsonResponse({'ok': True})

@csrf_exempt
def eliminar_componente(request):
    data = json.loads(request.body)
    try:
        ComponenteMaterial.objects.get(id=data.get('id')).delete()
        return JsonResponse({'ok': True})
    except:
        return JsonResponse({'ok': False, 'error': 'No se pudo eliminar'})
