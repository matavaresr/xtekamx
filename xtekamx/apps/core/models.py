from django.db import models

class Usuario(models.Model):
    TIPO_CHOICES = [
        (0, 'Cliente'),
        (1, 'Administrador'),
    ]
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    tipo = models.PositiveSmallIntegerField(choices=TIPO_CHOICES, default=0)

class Permiso(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

class UsuarioPermiso(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'permiso')

class TipoPaquete(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

class Hotel(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)

class Paquete(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    duracion_dias = models.IntegerField()
    precio_adulto = models.DecimalField(max_digits=10, decimal_places=2)
    precio_nino = models.DecimalField(max_digits=10, decimal_places=2)
    minimo_personas = models.IntegerField()
    maximo_personas = models.IntegerField()
    imagen_portada_url = models.TextField()
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    tipo_paquete = models.ForeignKey(TipoPaquete, on_delete=models.CASCADE)

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)

class ImagenUbicacion(models.Model):
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    url_imagen = models.TextField()
    descripcion = models.TextField()

class Actividad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

class ImagenActividad(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    url_imagen = models.TextField()
    descripcion = models.TextField()

class PaqueteActividad(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('paquete', 'actividad')

class Amenidad(models.Model):
    nombre = models.CharField(max_length=100)

class PaqueteAmenidad(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    amenidad = models.ForeignKey(Amenidad, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('paquete', 'amenidad')

class Reserva(models.Model):
    ESTADO_CHOICES = [
        (0, 'Pendiente'),
        (1, 'Confirmada'),
        (2, 'Cancelada'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cantidad_adultos = models.IntegerField()
    cantidad_ninos = models.IntegerField()
    total_pago = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.PositiveSmallIntegerField(choices=ESTADO_CHOICES, default=0)

class ConfiguracionSitio(models.Model):
    clave = models.CharField(max_length=100, primary_key=True)
    valor = models.TextField()
