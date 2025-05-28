from django.urls import path
from Admin.views.inicio import * 
from Admin.views.centros import * 
from Admin.views.materiales import * 


app_name = 'Admin'

urlpatterns = [ 
    path('', inicio, name='inicio'),
    
    # CENTROS
    path('centros/', centros, name='centros'),
    path('centros/guardar/', guardar_centro, name='guardar_centro'),
    path('centros/eliminar/', eliminar_centro, name='eliminar_centro'),
    
    # MATERIALES
    path('materiales/', materiales, name='materiales'),                     
    path('materiales/guardar/', guardar_material, name='guardar_material'),  
    path('materiales/eliminar/', eliminar_material, name='eliminar_material'), 
    
    path('materiales/componentes/<int:material_id>/', ver_componentes, name='ver_componentes'),
    path('materiales/componentes/guardar/', guardar_componente, name='guardar_componente'),
    path('materiales/componentes/eliminar/', eliminar_componente, name='eliminar_componente'),

    
    
]
