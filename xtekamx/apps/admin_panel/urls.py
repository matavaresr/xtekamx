from django.urls import path
from . import views  

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Panel principal
    path('login/', views.login, name='login'),  # Login
    path('crud/<str:modelo>/', views.crud, name='crud'),
     path('crud/<str:modelo>/eliminar/<str:pk>/', views.crud_eliminar, name='crud_eliminar'),
     path('crud/<str:modelo>/crear/', views.crud_crear, name='crud_crear'),
     path('crud/<str:modelo>/editar/<str:pk>/', views.crud_editar, name='crud_editar'),
     path('logout/', views.logout_view, name='logout')

]