from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import json
from Inicio.models import (
    EntradaMaterial, EntradaItem, MovimientoStock,
    OrdenCompra, OCItem, Almacen, ROH
)

# ===============================
# 📌 Entradas de Materiales
# ===============================

from django.db.models import Sum

def entradas(request):
    entradas = EntradaMaterial.objects.select_related('almacen', 'orden_compra').prefetch_related('items__material')

    ordenes = []
    for oc in OrdenCompra.objects.prefetch_related('items'):
        items = []

        for item in oc.items.all():
            ingresado = EntradaItem.objects.filter(oc_item_id=item.id).aggregate(total=Sum('cantidad'))['total'] or 0
            pendiente = max(item.cantidad - ingresado, 0)

            # 🔒 Solo agregamos ítems con pendiente > 0
            if pendiente > 0:
                items.append({
                    "id": item.id,
                    "descripcion": item.descripcion,
                    "cantidad": pendiente
                })

        # 🔒 Solo agregamos la OC si tiene al menos un ítem pendiente
        if items:
            ordenes.append({
                "id": oc.id,
                "items": items
            })

    almacenes = list(Almacen.objects.filter(nombre__icontains="Materias Primas").values('id', 'nombre'))

    return render(request, 'admin/entradas.html', {
        "entradas": entradas,
        "ordenes": ordenes,
        "almacenes": almacenes
    })





@csrf_exempt
def guardar_entrada(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        almacen_id = data.get('almacen_id')
        oc_id = data.get('orden_compra_id')
        items_data = data.get('items', [])

        if not almacen_id or not items_data:
            return JsonResponse({'ok': False, 'error': 'Faltan campos obligatorios.'})

        almacen = get_object_or_404(Almacen, id=almacen_id)
        oc = get_object_or_404(OrdenCompra, id=oc_id) if oc_id else None

        entrada = EntradaMaterial.objects.create(
            almacen=almacen,
            orden_compra=oc,
            comentario=data.get('comentario', '')
        )

        for item in items_data:
            oc_item = None
            cantidad_ingresada = int(item['cantidad'])

            if item.get('oc_item_id'):
                oc_item = get_object_or_404(OCItem, id=item['oc_item_id'])
                material = oc_item.solped_item.material

                total_previos = EntradaItem.objects.filter(oc_item=oc_item).aggregate(
                    total=models.Sum('cantidad')
                )['total'] or 0

                if total_previos + cantidad_ingresada > oc_item.cantidad:
                    entrada.delete()
                    return JsonResponse({
                        'ok': False,
                        'error': f"Supera lo ordenado: {oc_item.descripcion} máximo {oc_item.cantidad}, ya ingresado: {total_previos}."
                    })
            else:
                material = get_object_or_404(ROH, id=item['material_id'])

            # Crear item de entrada
            EntradaItem.objects.create(
                entrada=entrada,
                material=material,
                cantidad=cantidad_ingresada,
                oc_item=oc_item
            )

            # Movimiento stock (+)
            MovimientoStock.objects.create(
                almacen=almacen,
                material=material,
                cantidad=cantidad_ingresada,
                motivo="Entrada OC" if oc else "Entrada Manual",
                referencia=f"Entrada #{entrada.id}"
            )

            # ✅ Aumentar stock del almacen
            almacen.cantidad += cantidad_ingresada
            almacen.save()

        return JsonResponse({'ok': True})


@csrf_exempt
def eliminar_entrada(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        entrada_id = data.get('id')
        entrada = get_object_or_404(EntradaMaterial, id=entrada_id)

        for item in entrada.items.all():
            MovimientoStock.objects.create(
                almacen=entrada.almacen,
                material=item.material,
                cantidad=-item.cantidad,
                motivo="Reversión por eliminación de entrada",
                referencia=f"Entrada #{entrada.id}"
            )
            # ✅ Revertir stock
            entrada.almacen.cantidad -= item.cantidad
            entrada.almacen.save()

        entrada.delete()
        return JsonResponse({'ok': True})


# ===============================
# 📌 Movimientos de Stock (Transferencias)
# ===============================

from Inicio.models import Almacen, MovimientoStock, ROH
from django.db.models import Sum
from collections import defaultdict

def movimientos(request):
    movimientos = MovimientoStock.objects.select_related('almacen', 'material').order_by('-fecha')

    almacenes = list(
        Almacen.objects.filter(nombre__icontains="Materias Primas")
        .values('id', 'nombre')
    )

    materiales_ids_con_stock = (
        MovimientoStock.objects
        .values('material')
        .annotate(total=Sum('cantidad'))
        .filter(total__gt=0)
        .values_list('material', flat=True)
    )

    materiales = list(
        ROH.objects
        .filter(id__in=materiales_ids_con_stock)
        .values('id', 'nombre')
    )

    # ➕ Estructura adicional: stock por almacén (para filtrar en el modal)
    stock_qs = (
        MovimientoStock.objects
        .values('almacen_id', 'material__id', 'material__nombre')
        .annotate(cantidad=Sum('cantidad'))
        .filter(cantidad__gt=0)
    )

    stock_por_almacen = defaultdict(list)
    materiales_stock = []
    stock_disponible = {}
    
    for s in stock_qs:
        stock_por_almacen[s['almacen_id']].append({
            "id": s['material__id'],
            "nombre": s['material__nombre']
        })
        materiales_stock.append({
            "nombre": s['material__nombre'],
            "unidad": ROH.objects.get(id=s['material__id']).unidad_base,
            "almacen_id": s['almacen_id'],
            "cantidad": s['cantidad']
        })
        clave = f"{s['almacen_id']}_{s['material__id']}"
        stock_disponible[clave] = s['cantidad']

    return render(request, 'admin/movimientos.html', {
        "movimientos": movimientos,
        "almacenes": almacenes,
        "materiales": materiales,
        "materiales_stock": materiales_stock,
        "stock_por_almacen": dict(stock_por_almacen),
        "stock_disponible": stock_disponible
    })





@csrf_exempt
def guardar_movimiento(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        origen_id = data.get('origen_id')
        destino_id = data.get('destino_id')
        material_id = data.get('material_id')
        cantidad = data.get('cantidad')
        motivo = data.get('motivo', '')

        if not origen_id or not destino_id or not material_id or not cantidad:
            return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios.'})

        if origen_id == destino_id:
            return JsonResponse({'ok': False, 'error': 'Origen y destino no pueden ser iguales.'})

        origen = get_object_or_404(Almacen, id=origen_id)
        destino = get_object_or_404(Almacen, id=destino_id)
        material = get_object_or_404(ROH, id=material_id)

        cantidad_int = int(cantidad)

        # ✅ Verificar stock disponible
        if origen.cantidad < cantidad_int:
            return JsonResponse({'ok': False, 'error': 'Stock insuficiente en el almacén origen.'})

        # Salida (origen)
        MovimientoStock.objects.create(
            almacen=origen,
            material=material,
            cantidad=-cantidad_int,
            motivo=motivo or "Transferencia a otro almacén",
            referencia=f"Salida hacia {destino.nombre}"
        )
        origen.cantidad -= cantidad_int
        origen.save()

        # Entrada (destino)
        MovimientoStock.objects.create(
            almacen=destino,
            material=material,
            cantidad=cantidad_int,
            motivo=motivo or "Transferencia desde otro almacén",
            referencia=f"Entrada desde {origen.nombre}"
        )
        destino.cantidad += cantidad_int
        destino.save()

        return JsonResponse({'ok': True})
