from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from Inicio.models import (
    FERT,
    BOM,
    ROH,
    PlanProduccion,
    PlanProduccionDetalle,
    PlanProduccionInsumo,
    SOLPED, 
    SOLPEDItem,
    Sede, 
    Usuario,
)

def planificacion(request):
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
                } for bom in BOM.objects.filter(fert=f)
            ]
        })
    context = {
        'fert_list': ferts,
        'planes': PlanProduccion.objects.select_related('fert').prefetch_related('detalles', 'insumos')
    }
    return render(request, 'admin/planificacion.html', context)


@csrf_exempt
def guardar_plan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fert_id = data.get('fert_id')
        cantidad_fert = float(data.get('cantidad_fert'))
        cantidad_fert_con_extra = float(data.get('cantidad_fert_con_extra'))
        costo_insumos = float(data.get('costo_insumos'))
        costo_total_estimado = float(data.get('costo_total_estimado'))
        distribucion = data.get('distribucion', [])
        insumos = data.get('insumos', [])

        fert = get_object_or_404(FERT, id=fert_id)
        plan = PlanProduccion.objects.create(
            fert=fert,
            cantidad_fert=cantidad_fert,
            cantidad_fert_con_extra=cantidad_fert_con_extra,
            costo_insumos=costo_insumos,
            costo_total_estimado=costo_total_estimado
        )

        for det in distribucion:
            PlanProduccionDetalle.objects.create(
                plan=plan,
                mes=int(det['mes']),
                año=int(det['año']),
                cantidad_en_mes=float(det['cantidad'])
            )

        for ins in insumos:
            roh = get_object_or_404(ROH, id=int(ins['roh_id']))
            PlanProduccionInsumo.objects.create(
                plan=plan,
                roh=roh,
                cantidad_requerida=float(ins['cantidad_requerida']),
                costo_total=float(ins['costo_total'])
            )

        return JsonResponse({'ok': True})

@csrf_exempt
def eliminar_plan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plan_id = data.get('id')
        plan = get_object_or_404(PlanProduccion, id=plan_id)
        plan.delete()
        return JsonResponse({'ok': True})

# SOLPED

# ================================
# 📌 LISTA Y FORM DE SOLPED
# ================================

def solped(request):
    planes = []
    for plan in PlanProduccion.objects.select_related('fert').prefetch_related('insumos__roh', 'insumos__solped_items'):
        planes.append({
            "id": plan.id,
            "nombre": f"Plan #{plan.id}",
            "fert": plan.fert.nombre,
            "insumos": [
                {
                    "id": ins.id,
                    "roh_id": ins.roh.id,
                    "roh_nombre": ins.roh.nombre,
                    "unidad": ins.roh.unidad_base,
                    "pendiente": ins.solped_items.count() == 0,
                    "cantidad": ins.cantidad_requerida,
                    "costo_total": float(ins.costo_total)
                }
                for ins in plan.insumos.all()
            ]
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
            total_estimado=0  # Calculamos en loop
        )

        total = 0
        for item in items_data:
            roh = get_object_or_404(ROH, id=item['roh_id'])
            plan_insumo = None
            if item.get('plan_insumo_id'):
                plan_insumo = get_object_or_404(PlanProduccionInsumo, id=item['plan_insumo_id'])

            SOLPEDItem.objects.create(
                solped=solped,
                material=roh,
                cantidad=int(item['cantidad']),
                unidad=roh.unidad_base,
                costo_estimado=float(item['costo_estimado']),
                observacion=item.get('observacion', ''),
                plan_insumo=plan_insumo
            )
            total += float(item['costo_estimado'])

        solped.total_estimado = total
        solped.save()

        return JsonResponse({'ok': True})


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
