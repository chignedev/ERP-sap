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

def entradas(request):
    entradas = EntradaMaterial.objects.select_related('almacen', 'orden_compra').prefetch_related('items__material')

    ordenes = []
    for oc in OrdenCompra.objects.prefetch_related('items'):
        ordenes.append({
            "id": oc.id,
            "items": [
                {
                    "id": item.id,
                    "descripcion": item.descripcion,
                    "cantidad": item.cantidad
                }
                for item in oc.items.all()
            ]
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

def movimientos(request):
    movimientos = MovimientoStock.objects.select_related('almacen', 'material').order_by('-fecha')

    # ⚡️ IMPORTANTE: convertir almacenes a lista de dicts JSON-safe
    almacenes = list(
        Almacen.objects.filter(nombre__icontains="Materias Primas")
        .values('id', 'nombre', 'cantidad')  # añade 'cantidad' para mostrar stock
    )
    materiales = list(ROH.objects.values('id', 'nombre'))

    return render(request, 'admin/movimientos.html', {
        "movimientos": movimientos,
        "almacenes": almacenes,   # ✅ ahora lista de dicts JSON-safe
        "materiales": materiales, # ✅ lista de dicts JSON-safe
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
