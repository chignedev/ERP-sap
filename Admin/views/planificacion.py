from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from Inicio.models import (
    FERT, BOM, ROH,
    PlanVenta, PlanVentaDetalle,
    PlanProduccion, PlanProduccionDetalle,
    PlanCompra, PlanCompraItem,
    SOLPED, SOLPEDItem,
    Sede, 
    Usuario,
)

def planificacion(request):
    # Serializar todos los FERTs con su BOM (recetas)
    ferts = []
    for f in FERT.objects.all():
        ferts.append({
            'id': f.id,
            'nombre': f.nombre,
            'bom': [
                {
                    'roh_id': bom.roh.id,
                    'roh_nombre': bom.roh.nombre,
                    'unidad_base': bom.roh.unidad_base,
                    'cantidad_por_unidad': float(bom.cantidad),
                    'precio': float(bom.roh.precio)
                }
                for bom in BOM.objects.filter(fert=f)
            ]
        })

    # Obtener todos los planes con sus detalles serializados
    planes = PlanVenta.objects.select_related('fert').prefetch_related('detalles')
    planes_list = []
    for p in planes:
        p.detalles_serializados = [
            {
                'mes': d.mes,
                'año': d.año,
                'cantidad': float(d.cantidad)
            }
            for d in p.detalles.all()
        ]
        planes_list.append(p)

    context = {
        'fert_list': ferts,
        'planes': planes_list
    }
    return render(request, 'admin/planificacion.html', context)

@csrf_exempt
def guardar_plan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plan_id = data.get('id')  # puede venir o no
        fert_id = data['fert_id']
        cantidad_total = int(data['cantidad_total'])
        distribucion = data['distribucion']

        fert = get_object_or_404(FERT, id=fert_id)

        if plan_id:
            # 🛠️ Editar plan existente
            plan_venta = get_object_or_404(PlanVenta, id=plan_id)
            plan_venta.fert = fert
            plan_venta.cantidad_total = cantidad_total
            plan_venta.save()

            # Borrar detalles anteriores
            plan_venta.detalles.all().delete()

            # Borrar producción e insumos anteriores
            produccion_qs = PlanProduccion.objects.filter(venta=plan_venta)
            if produccion_qs.exists():
                produccion = produccion_qs.first()

                produccion.detalles.all().delete()

                compra_qs = PlanCompra.objects.filter(produccion=produccion)
                if compra_qs.exists():
                    compra = compra_qs.first()
                    compra.items.all().delete()
                    compra.delete()

                produccion.delete()

        else:
            # ➕ Crear nuevo plan
            plan_venta = PlanVenta.objects.create(fert=fert, cantidad_total=cantidad_total)

        # Crear nuevos detalles del plan
        for d in distribucion:
            PlanVentaDetalle.objects.create(
                plan=plan_venta,
                mes=int(d['mes']),
                año=int(d['año']),
                cantidad=int(d['cantidad'])
            )

        # Calcular producción (+10%)
        cantidad_produccion_total = int(cantidad_total * 1.10)
        plan_prod = PlanProduccion.objects.create(
            venta=plan_venta,
            fert=fert,
            cantidad_fert=cantidad_total,
            cantidad_fert_con_extra=cantidad_produccion_total,
            costo_insumos=0,
            costo_total_estimado=0
        )

        for d in distribucion:
            PlanProduccionDetalle.objects.create(
                plan=plan_prod,
                mes=int(d['mes']),
                año=int(d['año']),
                cantidad_en_mes=int(int(d['cantidad']) * 1.10)
            )

        # Calcular insumos y costos
        total_costo = 0
        compra = PlanCompra.objects.get_or_create(produccion=plan_prod)[0]
        for b in BOM.objects.filter(fert=fert):
            cantidad_total_insumo = cantidad_produccion_total * b.cantidad
            costo = cantidad_total_insumo * b.roh.precio
            total_costo += costo
            PlanCompraItem.objects.create(
                plan=compra,
                roh=b.roh,
                cantidad_comprar=int(cantidad_total_insumo),
                costo_total=costo
            )

        plan_prod.costo_insumos = total_costo
        plan_prod.costo_total_estimado = total_costo
        plan_prod.save()

        return JsonResponse({'ok': True})


# 🔴 ELIMINAR un plan
@csrf_exempt
def eliminar_plan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plan_id = data.get('id')
        plan_venta = get_object_or_404(PlanVenta, id=plan_id)

        # Borrar producción e insumos
        produccion_qs = PlanProduccion.objects.filter(venta=plan_venta)
        if produccion_qs.exists():
            produccion = produccion_qs.first()

            compra_qs = PlanCompra.objects.filter(produccion=produccion)
            if compra_qs.exists():
                compra = compra_qs.first()
                compra.items.all().delete()
                compra.delete()

            produccion.detalles.all().delete()
            produccion.delete()

        # Borrar detalles y plan
        plan_venta.detalles.all().delete()
        plan_venta.delete()

        return JsonResponse({'ok': True})
    
    
# SOLPED

# ================================
# 📌 LISTA Y FORM DE SOLPED
# ================================

def solped(request):
    planes = []

    # Obtenemos todos los Planes de Producción con sus FERT e insumos
    for plan in PlanProduccion.objects.select_related('fert', 'venta').prefetch_related('planes_compra__items__roh', 'planes_compra__items__solped_items'):
        insumos = []
        for plan_compra in plan.planes_compra.all():
            for item in plan_compra.items.all():
                insumos.append({
                    "id": item.id,
                    "roh_id": item.roh.id,
                    "roh_nombre": item.roh.nombre,
                    "unidad": item.roh.unidad_base,
                    "pendiente": item.solped_items.count() == 0,
                    "cantidad": item.cantidad_comprar,
                    "costo_total": float(item.costo_total)
                })

        planes.append({
            "id": plan.id,
            "nombre": f"Plan #{plan.id}",
            "fert": plan.fert.nombre,
            "insumos": insumos
        })

    return render(request, 'admin/solped.html', {
        "planes": planes,
        "solpeds": SOLPED.objects.select_related('centro', 'solicitante', 'plan_produccion').prefetch_related('items__material')
    })





# ================================
# 📌 GUARDAR SOLPED CON ITEMS
# ================================

@csrf_exempt
def guardar_solped(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        centro_id = data.get('centro_id')
        plan_id = data.get('plan_id')
        solicitante_id = data.get('solicitante_id')
        items_data = data.get('items', [])

        if not centro_id or not solicitante_id or not items_data:
            return JsonResponse({'ok': False, 'error': 'Centro, solicitante e items son obligatorios.'})

        centro = get_object_or_404(Sede, id=centro_id)
        solicitante = get_object_or_404(Usuario, id=solicitante_id)
        plan = None
        if plan_id:
            plan = get_object_or_404(PlanProduccion, id=plan_id)

        solped = SOLPED.objects.create(
            centro=centro,
            solicitante=solicitante,
            plan_produccion=plan,
            total_estimado=0  # Se calculará abajo
        )

        total = 0
        for item in items_data:
            roh = get_object_or_404(ROH, id=item['roh_id'])

            # ✅ Nuevo: obtener el PlanCompraItem si se envió plan_insumo_id
            plan_insumo = None
            if item.get('plan_insumo_id'):
                plan_insumo = get_object_or_404(PlanCompraItem, id=item['plan_insumo_id'])

            costo = float(item['costo_estimado'])
            cantidad = int(item['cantidad'])

            SOLPEDItem.objects.create(
                solped=solped,
                material=roh,
                cantidad=cantidad,
                unidad=roh.unidad_base,
                costo_estimado=costo,
                observacion=item.get('observacion', ''),
                plan_insumo=plan_insumo
            )
            total += costo

        solped.total_estimado = total
        solped.save()

        return JsonResponse({'ok': True})

    return JsonResponse({'ok': False, 'error': 'Método no permitido'})
# ================================
# 📌 ELIMINAR SOLPED COMPLETA
# ================================

@csrf_exempt
def eliminar_solped(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        solped_id = data.get('id')
        solped = get_object_or_404(SOLPED, id=solped_id)
        solped.delete()
        return JsonResponse({'ok': True})
