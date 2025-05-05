from django.contrib import admin
from .models import (
    Usuario, Cliente, Hotel, TipoPaquete, Paquete,
    ImagenPaquete, Ubicacion, Actividad, Amenidad,
    Reservacion, ConfiguracionSitio, ClienteReservacion,
    PaqueteUbicacion, PaqueteActividad, PaqueteAmenidad,
    Itinerario, Faq
)

admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(Hotel)
admin.site.register(TipoPaquete)
admin.site.register(Paquete)
admin.site.register(ImagenPaquete)
admin.site.register(Ubicacion)
admin.site.register(Actividad)
admin.site.register(Amenidad)
admin.site.register(Reservacion)
admin.site.register(ConfiguracionSitio)
admin.site.register(ClienteReservacion)
admin.site.register(PaqueteUbicacion)
admin.site.register(PaqueteActividad)
admin.site.register(PaqueteAmenidad)
admin.site.register(Itinerario)
admin.site.register(Faq)