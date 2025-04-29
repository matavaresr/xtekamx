from django.urls import path
from . import views  

urlpatterns = [
    path('', views.home, name='inicio'),  # Panel principal
    path('contacto', views.contacto, name='contacto'), 
    path('como_llegar', views.como_llegar, name='como_llegar'), 
    path('acerca_de', views.acerca_de, name='acerca_de'), 
    path('paquetes', views.paquetes, name='paquetes'),  # Vista general de paquetes
    path('paquetes/<int:id>/', views.paquete_unico, name='paquete_unico'),  # Paquete específico
    path('actividades', views.actividades, name='actividades'), 
    path('iniciar_sesion', views.iniciar_sesion, name='iniciar_sesion'),
    path('registro', views.registro, name='registro'), 
    path('terminosycondiciones', views.terminosycondiciones, name='terminosycondiciones'), 
]