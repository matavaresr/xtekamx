from django.contrib import admin
from .models import (
    Usuario, Permiso, UsuarioPermiso,
    TipoPaquete, Hotel, Paquete,
    Ubicacion, ImagenUbicacion,
    Actividad, ImagenActividad,
    PaqueteActividad, Amenidad,
    PaqueteAmenidad, Reserva,
    ConfiguracionSitio
)

# Regístralos en el panel de administración
admin.site.register(Usuario)
admin.site.register(Permiso)
admin.site.register(UsuarioPermiso)
admin.site.register(TipoPaquete)
admin.site.register(Hotel)
admin.site.register(Paquete)
admin.site.register(Ubicacion)
admin.site.register(ImagenUbicacion)
admin.site.register(Actividad)
admin.site.register(ImagenActividad)
admin.site.register(PaqueteActividad)
admin.site.register(Amenidad)
admin.site.register(PaqueteAmenidad)
admin.site.register(Reserva)
admin.site.register(ConfiguracionSitio)
