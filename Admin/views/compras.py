from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from Inicio.models import (
    SOLPED, SOLPEDItem,
    OrdenCompra, OCItem, OCEntregaProgramada,
    Proveedor, Usuario
)

# ✅ Lista de Proveedores
def proveedores(request):
    return render(request, 'admin/proveedores.html', {
        "proveedores": Proveedor.objects.all()
    })

# ✅ Guardar o editar Proveedor
@csrf_exempt
def guardar_proveedor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        nombre = data.get('nombre')
        ruc = data.get('ruc')
        direccion = data.get('direccion')
        telefono = data.get('telefono')
        email = data.get('email')
        contacto = data.get('contacto')

        if not nombre or not ruc:
            return JsonResponse({'ok': False, 'error': 'Nombre y RUC son obligatorios.'})

        if id:
            proveedor = get_object_or_404(Proveedor, id=id)
            proveedor.nombre = nombre
            proveedor.ruc = ruc
            proveedor.direccion = direccion
            proveedor.telefono = telefono
            proveedor.email = email
            proveedor.contacto = contacto
            proveedor.save()
        else:
            if Proveedor.objects.filter(ruc=ruc).exists():
                return JsonResponse({'ok': False, 'error': 'RUC ya registrado.'})
            Proveedor.objects.create(
                nombre=nombre,
                ruc=ruc,
                direccion=direccion,
                telefono=telefono,
                email=email,
                contacto=contacto
            )

        return JsonResponse({'ok': True})

# ✅ Eliminar Proveedor
@csrf_exempt
def eliminar_proveedor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        proveedor = get_object_or_404(Proveedor, id=id)
        proveedor.delete()
        return JsonResponse({'ok': True})


# 📌 Órdenes de Compra

def ordenes_compra(request):
    # ✅ Mostrar solo SOLPEDs que están aprobadas y que NO tengan OC
    solpeds = []
    for s in SOLPED.objects.filter(estado='aprobado').prefetch_related('items__material'):
        if not OrdenCompra.objects.filter(solped=s).exists():
            solpeds.append({
                "id": s.id,
                "estado": s.estado,
                "items": [
                    {
                        "id": item.id,
                        "material_nombre": item.material.nombre,
                        "cantidad": item.cantidad,
                    }
                    for item in s.items.all()
                ]
            })

    proveedores = list(Proveedor.objects.values('id', 'nombre'))

    ordenes = OrdenCompra.objects.select_related('solped', 'solicitante').prefetch_related('items__proveedor')

    return render(request, 'admin/ordenes_compra.html', {
        "solpeds": solpeds,
        "proveedores": proveedores,
        "ordenes": ordenes
    })


@csrf_exempt
def guardar_orden_compra(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        solped_id = data.get('solped_id')
        solicitante_id = data.get('solicitante_id')
        items_data = data.get('items', [])

        if not solped_id or not solicitante_id or not items_data:
            return JsonResponse({'ok': False, 'error': 'Faltan campos obligatorios.'})

        solped = get_object_or_404(SOLPED, id=solped_id)

        # 🔒 Validación: no usar SOLPED repetida
        if OrdenCompra.objects.filter(solped=solped).exists():
            return JsonResponse({'ok': False, 'error': 'Esta SOLPED ya tiene una Orden de Compra.'})

        solicitante = get_object_or_404(Usuario, id=solicitante_id)

        oc = OrdenCompra.objects.create(
            solped=solped,
            solicitante=solicitante,
            comentario=data.get('comentario', ''),
            total_estimado=0
        )

        total = 0
        for item in items_data:
            solped_item = get_object_or_404(SOLPEDItem, id=item['solped_item_id'])
            proveedor = get_object_or_404(Proveedor, id=item['proveedor_id'])
            oc_item = OCItem.objects.create(
                orden=oc,
                solped_item=solped_item,
                proveedor=proveedor,
                descripcion=solped_item.material.nombre,
                cantidad=solped_item.cantidad,
                unidad=solped_item.unidad,
                costo_estimado=solped_item.costo_estimado
            )
            total += solped_item.costo_estimado

            for entrega in item.get('entregas', []):
                OCEntregaProgramada.objects.create(
                    item=oc_item,
                    fecha_entrega=entrega['fecha'],
                    cantidad=int(entrega['cantidad'])
                )

        # ✅ Actualiza estado de SOLPED a "ordenado"
        solped.estado = "ordenado"
        solped.save()

        oc.total_estimado = total
        oc.save()

        return JsonResponse({'ok': True})

@csrf_exempt
def eliminar_orden_compra(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        oc_id = data.get('id')
        oc = get_object_or_404(OrdenCompra, id=oc_id)

        # ✅ Cuando se elimina OC, volver SOLPED a "aprobado"
        solped = oc.solped
        solped.estado = "aprobado"
        solped.save()

        oc.delete()
        return JsonResponse({'ok': True})
