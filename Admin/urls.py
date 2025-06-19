from django.urls import path

# Importa todas las vistas necesarias
from Admin.views.inicio import *
from Admin.views.centros import *
from Admin.views.materiales import *
from Admin.views.planificacion import *
from Admin.views.aprobacion import *
from Admin.views.compras import *
from Admin.views.almacen import *

app_name = 'Admin'

urlpatterns = [
    # DASHBOARD
    path('', inicio, name='inicio'),

    # CENTROS
    path('sedes/', sedes, name='sedes'),
    path('sedes/guardar/', guardar_sede, name='guardar_sede'),
    path('sedes/eliminar/', eliminar_sede, name='eliminar_sede'),

    path('almacenes/', almacenes, name='almacenes'),
    path('almacenes/guardar/', guardar_almacen, name='guardar_almacen'),
    path('almacenes/eliminar/', eliminar_almacen, name='eliminar_almacen'),

    # MATERIALES
    path('materiales/', materiales, name='materiales'),
    path('materiales/guardar/', guardar_material, name='guardar_material'),
    path('materiales/eliminar/', eliminar_material, name='eliminar_material'),

    path('fert/', fert, name='fert'),
    path('fert/guardar/', guardar_fert, name='guardar_fert'),
    path('fert/eliminar/', eliminar_fert, name='eliminar_fert'),

    path('bom/', bom, name='bom'),
    path('bom/guardar/', guardar_bom, name='guardar_bom'),
    path('bom/eliminar/', eliminar_bom, name='eliminar_bom'),


    # PLANIFICACIÓN
    path('planificacion/', planificacion, name='planificacion'),
    path('planificacion/guardar/', guardar_plan, name='guardar_plan'),
    path('planificacion/eliminar/', eliminar_plan, name='eliminar_plan'),

    path('solped/', solped, name='solped'),
    path('solped/guardar/', guardar_solped, name='guardar_solped'),
    path('solped/eliminar/', eliminar_solped, name='eliminar_solped'),

    # APROBACIÓN
    path('aprobacion/', aprobacion, name='aprobacion'),
    path('aprobacion/guardar/', guardar_aprobacion, name='guardar_aprobacion'),

    # COMPRAS
    path('proveedores/', proveedores, name='proveedores'),
    path('proveedores/guardar/', guardar_proveedor, name='guardar_proveedor'),
    path('proveedores/eliminar/', eliminar_proveedor, name='eliminar_proveedor'),

    path('ordenes_compra/', ordenes_compra, name='ordenes_compra'),
    path('ordenes_compra/guardar/', guardar_orden_compra, name='guardar_orden_compra'),
    path('ordenes_compra/eliminar/', eliminar_orden_compra, name='eliminar_orden_compra'),

    # ALMACÉN
    path('entradas/', entradas, name='entradas'),
    path('entradas/guardar/', guardar_entrada, name='guardar_entrada'),
    path('entradas/eliminar/', eliminar_entrada, name='eliminar_entrada'),

    path('movimientos/', movimientos, name='movimientos'),
    path('movimientos/guardar/', guardar_movimiento, name='guardar_movimiento'),
]
