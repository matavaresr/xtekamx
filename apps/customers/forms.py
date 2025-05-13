from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from apps.core.models import Reservacion, Paquete, Cliente
from django.core.validators import validate_email
from .utils import obtener_fechas_bloqueadas, optimizar_rangos_bloqueados 

class ReservacionForm(forms.ModelForm):
    paquete_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Reservacion
        fields = [
            'fecha_inicio',
            'cantidad_adultos',
            'cantidad_ninos',
        ]
        # Personalizar los mensajes de error de los campos requeridos
        error_messages = {
            'fecha_inicio': {
                'required': 'La fecha de inicio es obligatoria.',
            },
            'cantidad_adultos': {
                'required': 'El número de adultos es obligatorio.',
            },
            'cantidad_ninos': {
                'required': 'El número de niños es obligatorio, si se aplica.',
            },
        }

    def __init__(self, *args, **kwargs):
        self.paquete = None
        super().__init__(*args, **kwargs)
        
        # Hacer que cantidad_ninos no sea obligatorio
        self.fields['cantidad_ninos'].required = False

    def clean(self):
        cleaned_data = super().clean()

        fecha_inicio_str = self.data.get('fecha_inicio')  # Viene como string
        cantidad_adultos = cleaned_data.get('cantidad_adultos')
        cantidad_ninos = cleaned_data.get('cantidad_ninos')
        paquete_id = self.data.get('paquete_id')

        # Si no viene cantidad_ninos, asumir 0
        if cantidad_ninos in [None, '']:
            cantidad_ninos = 0
            cleaned_data['cantidad_ninos'] = 0

        # Validar paquete
        if not paquete_id:
            raise ValidationError("Debe seleccionar un paquete.")
        try:
            self.paquete = Paquete.objects.get(id=paquete_id)
        except Paquete.DoesNotExist:
            raise ValidationError("El paquete no existe.")

        # Validar fecha_inicio
        if not fecha_inicio_str:
            raise ValidationError("Debes seleccionar una fecha de inicio válida.")
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Formato de fecha inválido. Debe ser YYYY-MM-DD.")

        # Validar que la fecha de inicio sea posterior a la fecha actual
        if fecha_inicio <= timezone.now().date():
            raise ValidationError("La fecha de inicio debe ser posterior a hoy.")

        # Calcular fecha_fin
        fecha_fin = fecha_inicio + timedelta(days=self.paquete.duracion_dias - 1)

        # Verificar conflictos de reservación
        conflicto = Reservacion.objects.filter(
            paquete=self.paquete,
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio
        ).exists()
        if conflicto:
            raise ValidationError("Ya existe una reservación en ese rango de fechas para este paquete.")

        # Validar número de personas
        total_personas = (cantidad_adultos or 0) + (cantidad_ninos or 0)
        if total_personas < self.paquete.minimo_personas or total_personas > self.paquete.maximo_personas:
            raise ValidationError(
                f'La cantidad total de personas ({total_personas}) debe estar entre '
                f'{self.paquete.minimo_personas} y {self.paquete.maximo_personas}.'
            )

        # Guardar valores transformados en cleaned_data
        cleaned_data['fecha_inicio'] = fecha_inicio
        cleaned_data['fecha_fin'] = fecha_fin
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.paquete = self.paquete
        instance.fecha_fin = instance.fecha_inicio + timedelta(days=self.paquete.duracion_dias - 1)
        instance.total_pago = (
            self.paquete.precio_adulto * instance.cantidad_adultos +
            self.paquete.precio_nino * (instance.cantidad_ninos or 0)  # Aseguramos que cantidad_ninos sea 0 si no existe
        )
        instance.estado = 1
        if commit:
            instance.save()
        return instance


class ClienteForm(forms.ModelForm):
    email = forms.CharField(
        error_messages={'required': 'El correo electrónico es obligatorio.'}  # Validación personalizada para el correo
    )
    telefono = forms.CharField(
        error_messages={'required': 'El número de teléfono es obligatorio.'}  # Validación personalizada para el teléfono
    )
    nombre = forms.CharField(
        error_messages={'required': 'El nombre es obligatorio.'}  # Validación personalizada para el nombre
    )
    apellido = forms.CharField(
        error_messages={'required': 'El apellido es obligatorio.'}  # Validación personalizada para el apellido
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono']

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        apellido = cleaned_data.get('apellido')
        telefono = cleaned_data.get('telefono')
        email = cleaned_data.get('email')

        # Validar nombre
        if nombre and not nombre[0].isupper():
            self.add_error('nombre', "El nombre debe comenzar con mayúscula.")

        # Validar apellido
        if apellido and not apellido[0].isupper():
            self.add_error('apellido', "El apellido debe comenzar con mayúscula.")

        # Validar teléfono
        if telefono and len(telefono) < 10:
            self.add_error('telefono', "El número de teléfono debe tener al menos 10 dígitos.")

        # Validar email
        if email:
            try:
                validate_email(email)  # Verifica que el email tenga formato válido
            except ValidationError:
                self.add_error('email', "Ingresa un correo electrónico válido.")

        return cleaned_data
