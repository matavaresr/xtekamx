import re
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

# === VALIDADORES COMUNES ===

def validar_nombre_sin_numeros_y_mayuscula(value):
    if not value[0].isupper():
        raise ValidationError("El nombre debe iniciar con mayúscula.")
    if any(char.isdigit() for char in value):
        raise ValidationError("El nombre no debe contener números.")

def validar_usuario(value):
    if not re.search(r'[a-zA-Z]', value) or not re.search(r'\d', value):
        raise ValidationError("El usuario debe contener al menos una letra y un número.")

def validar_contrasena(value):
    if (not re.search(r'[A-Za-z]', value) or
        not re.search(r'\d', value) or
        not re.search(r'[\W_]', value)):
        raise ValidationError("La contraseña debe tener al menos una letra, un número y un carácter especial.")

def validar_telefono(value):
    if not re.fullmatch(r'\d{10}|\d{12}', value):
        raise ValidationError("El teléfono debe tener exactamente 10 o 12 dígitos numéricos.")

# === MODELOS ===

class Usuario(models.Model):
    TIPO_CHOICES = [
        (1, 'Administrador'),
        (2, 'Supervisor'),
        (3, 'Empleado'),
    ]

    usuario = models.CharField(max_length=100, validators=[validar_usuario])
    email = models.EmailField(unique=True,error_messages={'invalid': 'Por favor, ingresa un correo electrónico válido.'})
    contrasena = models.CharField(max_length=255, validators=[validar_contrasena])
    tipo = models.SmallIntegerField(choices=TIPO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.tipo not in dict(self.TIPO_CHOICES):
            raise ValidationError({'tipo': 'Tipo de usuario no válido.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Cliente(models.Model):
    nombre = models.CharField(max_length=100, validators=[validar_nombre_sin_numeros_y_mayuscula])
    apellido = models.CharField(max_length=100, validators=[validar_nombre_sin_numeros_y_mayuscula])
    email = models.EmailField(error_messages={'invalid': 'Por favor, ingresa un correo electrónico válido.'})
    telefono = models.CharField(max_length=20, validators=[validar_telefono])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Hotel(models.Model):
    nombre = models.CharField(max_length=100, validators=[validar_nombre_sin_numeros_y_mayuscula])
    ubicacion = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class TipoPaquete(models.Model):
    nombre = models.CharField(max_length=100, unique=True, validators=[validar_nombre_sin_numeros_y_mayuscula])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Paquete(models.Model):
    nombre = models.CharField(max_length=100, validators=[validar_nombre_sin_numeros_y_mayuscula])
    descripcion = models.TextField()
    duracion_dias = models.SmallIntegerField(validators=[MinValueValidator(1)])
    precio_adulto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    precio_nino = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    minimo_personas = models.SmallIntegerField(validators=[MinValueValidator(1)])
    maximo_personas = models.SmallIntegerField(validators=[MinValueValidator(1)])
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)
    tipo_paquete = models.ForeignKey(TipoPaquete, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.maximo_personas < self.minimo_personas:
            raise ValidationError("El número máximo de personas no puede ser menor que el mínimo.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ImagenPaquete(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    url_imagen = models.TextField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    es_portada = models.BooleanField(default=False)
    public_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100, validators=[validar_nombre_sin_numeros_y_mayuscula])
    descripcion = models.TextField()
    url_portada = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Actividad(models.Model):
    nombre = models.CharField(max_length=100, validators=[validar_nombre_sin_numeros_y_mayuscula])
    url_portada = models.TextField()
    descripcion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Amenidad(models.Model):
    nombre = models.CharField(max_length=100, validators=[validar_nombre_sin_numeros_y_mayuscula])
    created_at = models.DateTimeField(auto_now_add=True)


class Reservacion(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cantidad_adultos = models.SmallIntegerField(validators=[MinValueValidator(1)])
    cantidad_ninos = models.SmallIntegerField(validators=[MinValueValidator(0)])
    total_pago = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
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
    estado = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])

    class Meta:
        unique_together = ('paquete', 'amenidad')


class Itinerario(models.Model):
    titulo = models.CharField(max_length=100, default='Día sin título')
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100, default='Dia sin título')
    dia = models.SmallIntegerField()
    descripcion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Faq(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    pregunta = models.TextField()
    respuesta = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
