from django.shortcuts import render
from django.contrib.auth import get_user_model
from Inicio.models import (
    Sede, ROH, FERT, BOM, PlanProduccion, SOLPED,
    Proveedor, OrdenCompra, EntradaMaterial
)

def inicio(request):
    Usuario = get_user_model()

    total_roh = ROH.objects.count()
    total_fert = FERT.objects.count()
    total_boms = BOM.objects.count()
    total_planes = PlanProduccion.objects.count()

    contexto = {
        'resumen': [
            ('Usuarios', Usuario.objects.count()),
            ('Sedes', Sede.objects.count()),
            ('ROHs', total_roh),
            ('FERTs', total_fert),
            ('Materiales en BOMs', total_boms),
            ('Planes', total_planes),
            ('SOLPEDs', SOLPED.objects.count()),
            ('Proveedores', Proveedor.objects.count()),
            ('Órdenes Compra', OrdenCompra.objects.count()),
            ('Entradas Material', EntradaMaterial.objects.count()),
        ],
        'total_roh': total_roh,
        'total_fert': total_fert,
        'total_boms': total_boms,
        'total_planes': total_planes,
    }

    return render(request, 'admin/inicio.html', contexto)
