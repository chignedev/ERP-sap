from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from Inicio.models import ROH, FERT, BOM, Sede, Almacen

# ================================
# 📌 CRUD de Materiales ROH
# ================================

def materiales(request):
    context = {
        'materiales': ROH.objects.select_related('centro', 'almacen').all(),
        'sedes': Sede.objects.all()
    }
    return render(request, 'admin/materiales.html', context)

@csrf_exempt
def guardar_material(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        codigo = data.get('codigo')
        nombre = data.get('nombre')
        unidad_base = data.get('unidad_base', 'KG')
        precio = data.get('precio')
        centro_id = data.get('centro_id')

        if not codigo or not nombre or not precio or not centro_id:
            return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios.'})

        centro = get_object_or_404(Sede, id=centro_id)

        # Buscar automáticamente el almacén de Materias Primas en esa sede
        almacen_mp = centro.almacenes.filter(nombre__icontains="Materias Primas").first()
        if not almacen_mp:
            return JsonResponse({'ok': False, 'error': 'No se encontró un Almacén de Materias Primas para la sede seleccionada.'})

        if id:
            material = get_object_or_404(ROH, id=id)
            material.codigo = codigo
            material.nombre = nombre
            material.unidad_base = unidad_base
            material.precio = precio
            material.centro = centro
            material.almacen = almacen_mp
            material.save()
        else:
            if ROH.objects.filter(codigo=codigo).exists():
                return JsonResponse({'ok': False, 'error': 'El código ya está registrado.'})
            ROH.objects.create(
                codigo=codigo,
                nombre=nombre,
                unidad_base=unidad_base,
                precio=precio,
                centro=centro,
                almacen=almacen_mp
            )
        return JsonResponse({'ok': True})


@csrf_exempt
def eliminar_material(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        try:
            material = get_object_or_404(ROH, id=id)
            material.delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})

# ================================
# 📌 CRUD de Materiales FERT
# ================================

def fert(request):
    context = {
        'fert_list': FERT.objects.select_related('centro').all(),
        'sedes': Sede.objects.all()
    }
    return render(request, 'admin/fert.html', context)

@csrf_exempt
def guardar_fert(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        codigo = data.get('codigo')
        nombre = data.get('nombre')
        unidad_base = data.get('unidad_base', 'KG')
        precio = data.get('precio')
        centro_id = data.get('centro_id')

        if not codigo or not nombre or not precio or not centro_id:
            return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios.'})

        centro = get_object_or_404(Sede, id=centro_id)

        # 🔑 Buscar automáticamente el Almacén de Producto Terminado en esa sede
        almacen_pt = centro.almacenes.filter(nombre__icontains="Producto Terminado").first()
        if not almacen_pt:
            return JsonResponse({'ok': False, 'error': 'No se encontró un Almacén de Producto Terminado para la sede seleccionada.'})

        if id:
            fert = get_object_or_404(FERT, id=id)
            fert.codigo = codigo
            fert.nombre = nombre
            fert.unidad_base = unidad_base
            fert.precio = precio
            fert.centro = centro
            fert.almacen = almacen_pt   # ✅ Guardar referencia
            fert.save()
        else:
            if FERT.objects.filter(codigo=codigo).exists():
                return JsonResponse({'ok': False, 'error': 'El código ya está registrado.'})
            FERT.objects.create(
                codigo=codigo,
                nombre=nombre,
                unidad_base=unidad_base,
                precio=precio,
                centro=centro,
                almacen=almacen_pt   # ✅ Guardar referencia
            )
        return JsonResponse({'ok': True})


@csrf_exempt
def eliminar_fert(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        try:
            fert = get_object_or_404(FERT, id=id)
            fert.delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})

# ================================
# 📌 CRUD de BOM (FERT + lista ROH)
# ================================

def bom(request):
    context = {
        'fert_list': FERT.objects.select_related('centro').all(),
        'roh_list': ROH.objects.select_related('centro').all(),
        'bom_list': BOM.objects.select_related('fert', 'roh').all(),
        'sedes': Sede.objects.all()
    }
    return render(request, 'admin/bom.html', context)

@csrf_exempt
def guardar_bom(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fert_id = data.get('fert_id')
        roh_id = data.get('roh_id')
        cantidad = data.get('cantidad')

        if not fert_id or not roh_id or not cantidad:
            return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios.'})

        fert = get_object_or_404(FERT, id=fert_id)
        roh = get_object_or_404(ROH, id=roh_id)

        # Crear o actualizar la relación BOM
        bom_obj, created = BOM.objects.get_or_create(
            fert=fert,
            roh=roh,
            defaults={'cantidad': cantidad}
        )
        if not created:
            bom_obj.cantidad = cantidad
            bom_obj.save()

        return JsonResponse({'ok': True})

@csrf_exempt
def eliminar_bom(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fert_id = data.get('fert_id')
        roh_id = data.get('roh_id')
        try:
            bom_obj = BOM.objects.get(fert_id=fert_id, roh_id=roh_id)
            bom_obj.delete()
            return JsonResponse({'ok': True})
        except BOM.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'La relación BOM no existe.'})
