from django.urls import path
from .views import envio_correo_contacto

urlpatterns = [
    path('enviar-correo-contacto/', envio_correo_contacto, name='enviar_correo_contacto'),
]