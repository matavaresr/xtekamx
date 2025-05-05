from django.urls import path
from . import views  

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Panel principal
    path('login/', views.login, name='login'),  # Login
    path('crud/<str:modelo>/', views.crud, name='crud'),
    path('crud/<str:modelo>/eliminar/<str:pk>/', views.crud_eliminar, name='crud_eliminar'),
    path('crud/<str:modelo>/crear/', views.crud_crear, name='crud_crear'),
    path('crud/<str:modelo>/editar/<str:pk>/', views.crud_editar, name='crud_editar'),
    path('paquetes/', views.paquetes_list, name='paquetes_list'),
    path('crear-paquete/', views.crear_paquete, name='crear_paquete'),
    path('eliminar-paquete/<int:paquete_id>/', views.eliminar_paquete, name='eliminar_paquete'),
    path('paquete-detalle/<int:paquete_id>/', views.paquete_detalle, name='paquete_detalle'),
    path('guardar-actividades/<int:paquete_id>/', views.guardar_actividades_paquete, name='guardar_actividades_paquete'),
    path('guardar-amenidades/<int:paquete_id>/', views.guardar_amenidades_paquete, name='guardar_amenidades_paquete'),
    path('guardar-ubicaciones/<int:paquete_id>/', views.guardar_ubicaciones_paquete, name='guardar_ubicaciones_paquete'),
    path('logout/', views.logout_view, name='logout'),
    path('imagenes/listar/', views.listar_imagenes, name='listar_imagenes'),
    path('imagenes/subir/', views.subir_imagen, name='subir_imagen'),
    path('imagenes/eliminar/', views.eliminar_imagen, name='eliminar_imagen'),
    path('imagenes/actualizar/', views.reemplazar_imagen, name='reemplazar_imagen'),
    path('guardar-imagen/', views.guardar_imagen_paquete, name='guardar_imagen'),
]