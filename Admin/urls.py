from django.urls import path
from Admin.views.inicio import * 


app_name = 'Admin'

urlpatterns = [ 
    path('', inicio, name='inicio'),
    
]
