from django.urls import path
from . import views  
from .views import PaqueteListView, PaqueteDetailView

urlpatterns = [
    path('', views.home, name='inicio'),  # Panel principal
    path('contacto', views.contacto, name='contacto'), 
    path('como_llegar', views.como_llegar, name='como_llegar'), 
    path('acerca_de', views.acerca_de, name='acerca_de'), 
    path('paquetes/', PaqueteListView.as_view(), name='paquetes'),  # ← el name es clave
    path('paquetes/<int:pk>/', PaqueteDetailView.as_view(), name='detalle_paquete'),   
    path('actividades', views.actividades, name='actividades'),  
    path('terminosycondiciones', views.terminosycondiciones, name='terminosycondiciones'), 
    path('ajax/reservar/', views.guardar_reservacion_ajax, name='guardar_reservacion_ajax'),
]