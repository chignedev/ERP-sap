from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from Inicio.models import SOLPED, SOLPEDItem

def aprobacion(request):
    solpeds = SOLPED.objects.select_related('centro', 'solicitante', 'plan_produccion').prefetch_related('items__material').filter(estado='pendiente')
    return render(request, 'admin/aprobacion.html', {
        "solpeds": solpeds
    })

@csrf_exempt
def guardar_aprobacion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        solped_id = data.get('id')
        action = data.get('action')

        solped = get_object_or_404(SOLPED, id=solped_id)

        if action == 'aprobar':
            solped.estado = 'aprobado'

        elif action == 'rechazar':
            solped.estado = 'rechazado'

            # ✅ Liberar los insumos del plan: eliminamos referencia plan_insumo
            for item in solped.items.filter(plan_insumo__isnull=False):
                item.plan_insumo = None
                item.save()

        else:
            return JsonResponse({'ok': False, 'error': 'Acción no válida.'})

        solped.save()
        return JsonResponse({'ok': True})
