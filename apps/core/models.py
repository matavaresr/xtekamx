from django.db import models

class Usuario(models.Model):
    
    TIPO_CHOICES = [
        (1, 'Administrador'),
        (2, 'Supervisor'),
        (3, 'Empleado'),
    ]
    
    usuario = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    tipo = models.SmallIntegerField(choices=TIPO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Hotel(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class TipoPaquete(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Paquete(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    duracion_dias = models.SmallIntegerField()
    precio_adulto = models.DecimalField(max_digits=10, decimal_places=2)
    precio_nino = models.DecimalField(max_digits=10, decimal_places=2)
    minimo_personas = models.SmallIntegerField()
    maximo_personas = models.SmallIntegerField()
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)
    tipo_paquete = models.ForeignKey(TipoPaquete, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ImagenPaquete(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    url_imagen = models.TextField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    es_portada = models.BooleanField(default=False)
    public_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    url_portada = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Actividad(models.Model):
    nombre = models.CharField(max_length=100)
    url_portada = models.TextField()
    descripcion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Amenidad(models.Model):
    nombre = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Reservacion(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cantidad_adultos = models.SmallIntegerField()
    cantidad_ninos = models.SmallIntegerField()
    total_pago = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class ConfiguracionSitio(models.Model):
    clave = models.CharField(max_length=100, primary_key=True)
    valor = models.TextField()

class ClienteReservacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('cliente', 'reservacion')

class PaqueteUbicacion(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('paquete', 'ubicacion')

class PaqueteActividad(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('paquete', 'actividad')

class PaqueteAmenidad(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    amenidad = models.ForeignKey(Amenidad, on_delete=models.CASCADE)
    estado = models.SmallIntegerField()

    class Meta:
        unique_together = ('paquete', 'amenidad')

class Itinerario(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    dia = models.SmallIntegerField()
    descripcion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Faq(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    pregunta = models.TextField()
    respuesta = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
