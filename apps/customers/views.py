import json
from datetime import datetime, timedelta

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.utils.dateformat import format

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm

from django.views.generic import ListView, DetailView

from .forms import ReservacionForm, ClienteForm

from apps.core.services.email_service import enviar_correo_reservacion
from .utils import obtener_fechas_bloqueadas, optimizar_rangos_bloqueados
from django_ratelimit.decorators import ratelimit


from apps.core.models import (
    Actividad, Paquete, ImagenPaquete, TipoPaquete, Itinerario,
    Cliente, Reservacion, ClienteReservacion, Amenidad, Ubicacion, Faq
)


# Página principal
def home(request):
    testimonios = [
        {
            "titulo": "Excelente experiencia",
            "descripcion": "Quiero agradecer a mis amigos de Xteka.mx por invitarme a esta aventura. Disfruté mucho de todas las atracciones, actividades y servicios que me brindaron. Les recomiendo visitar la Cascada de El Meco, pues es un lugar para salir un poco de tu zona de confort y desconectarse de todo. ¡Servicio 10/10!",
            "instagram": "@fitnessalvarezz (120,000 seguidores)",
            "ubicacion": "Monterrey, Nuevo León, México",
            "imagen": "https://res.cloudinary.com/dtzil5dwl/image/upload/v1746521206/testimonial_3_iqupsh.png"
        },
        {
            "titulo": "Un servicio inigualable",
            "descripcion": "En nuestro viaje por México, paramos en la Huasteca y nos encontramos con Olaff, un guía de Xteka.mx. Nos llevó a realizar actividades en las hermosas aguas color turquesa y a las cascadas, y fue muy atento en todo momento. Nos llevamos buenas tomas y pueden encontrar el video que realizamos en Instagram y TikTok. ¡100% recomendado tomar un tour con ellos!",
            "instagram": "viajando.conlopuesto (128,000 seguidores)",
            "ubicacion": "España",
            "imagen": "https://res.cloudinary.com/dtzil5dwl/image/upload/v1746521206/testimonial_2_zizluj.png"
        },
        {
            "titulo": "Atención espectacular",
            "descripcion": "Amigos, vivan la experiencia de la Huasteca en El Naranjo, San Luis Potosí. Hagan sus recorridos con guías capacitados siempre y recuerden traer su chaleco salvavidas en todo momento. Pero sobre todo, disfruten de estos maravillosos sitios naturales.",
            "instagram": "@aztecasanluispotosi @jorgelopez_perez (6,641 seguidores)",
            "ubicacion": "San Luis Potosí, México",
            "imagen": "https://res.cloudinary.com/dtzil5dwl/image/upload/v1746521206/testimonial_1_cx4ydj.png"
        }
    ]

    return render(request, 'customers/index.html', {'testimonios': testimonios})

# Página de contacto
def contacto(request):
    return render(request, 'customers/contacto.html')

# Página de cómo llegar
def como_llegar(request):
    return render(request, 'customers/como_llegar.html')

# Página acerca de
def acerca_de(request):
    return render(request, 'customers/acerca_de.html')

# Vista de un paquete específico
def paquete_unico(request, id):
    # Aquí podrías obtener el paquete específico desde la base de datos
    paquete = {"id": id, "nombre": f"Paquete {id}"}
    return render(request, 'customers/paquete_unico.html', {'paquete': paquete})

# Página de actividades
def actividades(request):
    actividades_all = Actividad.objects.all()
    cache.set('actividades_lista', actividades, 60 * 15)  # 15 minutos
    return render(request, 'customers/actividades.html', {'actividades': actividades_all})

# Página acerca de
def terminosycondiciones(request):
    return render(request, 'customers/terminosycondiciones.html')

class PaqueteListView(ListView):
    model = Paquete
    template_name = 'customers/paquetes.html'
    context_object_name = 'paquetes'
    paginate_by = 10

    def get_queryset(self):
        queryset = Paquete.objects.all().select_related('tipo_paquete', 'hotel').prefetch_related(
            Prefetch('imagenpaquete_set', queryset=ImagenPaquete.objects.filter(es_portada=True))
        )

        tipo_paquete = self.request.GET.get('tipo_paquete')
        precio_max = self.request.GET.get('precio_adulto')
        tiene_hotel = self.request.GET.get('hotel')

        if tipo_paquete:
            queryset = queryset.filter(tipo_paquete_id=tipo_paquete)
        if precio_max:
            try:
                queryset = queryset.filter(precio_adulto__lte=float(precio_max))
            except ValueError:
                pass
        if tiene_hotel == '1':
            queryset = queryset.filter(hotel__isnull=False)
        elif tiene_hotel == '0':
            queryset = queryset.filter(hotel__isnull=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = TipoPaquete.objects.all()
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string("customers/components/paquetes_grid.html", context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)

def paquete_detail(request, pk):
    paquete = get_object_or_404(Paquete, pk=pk)

    # Fechas bloqueadas optimizadas
    rangos_originales = obtener_fechas_bloqueadas(paquete)
    rangos_optim = optimizar_rangos_bloqueados(rangos_originales, paquete.duracion_dias)

    context = {
        'paquete': paquete,
        'fechas_bloqueadas': rangos_optim,
        'amenidades': Amenidad.objects.filter(
            paqueteamenidad__paquete=paquete,
            paqueteamenidad__estado=1
        ),
        'ubicaciones': Ubicacion.objects.filter(paqueteubicacion__paquete=paquete),
        'actividades': Actividad.objects.filter(paqueteactividad__paquete=paquete),
        'faqs': Faq.objects.filter(paquete_id=paquete.id).order_by('id'),
        'itinerarios': Itinerario.objects.filter(paquete_id=paquete.id).order_by('dia'),
    }

    return render(request, 'customers/paquete_unico.html', context)

@csrf_exempt
@ratelimit(key='ip', rate='5/m', block=True)
def guardar_reservacion_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

    cliente_form = ClienteForm(request.POST)
    reservacion_form = ReservacionForm(request.POST)

    

    if cliente_form.is_valid() and reservacion_form.is_valid():
        email = cliente_form.cleaned_data['email']
        telefono = cliente_form.cleaned_data['telefono']

        # Buscar cliente existente
        cliente = Cliente.objects.filter(email=email).first()

        if cliente:
            if cliente.telefono != telefono:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El número de teléfono no coincide con el registrado para este correo.',
                    'cliente_errors': {
                        'telefono': [{'message': 'Teléfono no coincide con el registrado.', 'code': 'invalid'}]
                    }
                }, status=400)
        else:
            # Crear nuevo cliente si no existe
            cliente = cliente_form.save()

        # Guardar la reservación
        reservacion = reservacion_form.save(commit=False)
        reservacion.cliente = cliente
        reservacion.save()

        ClienteReservacion.objects.create(cliente=cliente, reservacion=reservacion)

        # Enviar correo
        enviar_correo_reservacion(cliente.email, {
            'nombre_cliente': cliente.nombre,
            'paquete_nombre': reservacion.paquete.nombre,
            'fecha_inicio': reservacion.fecha_inicio,
            'fecha_fin': reservacion.fecha_fin,
            'cantidad_adultos': reservacion.cantidad_adultos,
            'cantidad_ninos': reservacion.cantidad_ninos,
            'total_pago': reservacion.total_pago,
        })

        return JsonResponse({'status': 'success', 'message': 'Reservación creada correctamente, recibiras un correo con tu información.'})

    return JsonResponse({
        'status': 'error',
        'message': 'Hubo errores en el formulario.',
        'cliente_errors': cliente_form.errors.get_json_data(),
        'reservacion_errors': reservacion_form.errors.get_json_data(),
    }, status=400)

def fechas_bloqueadas_ajax(request, paquete_id):
    try:
        paquete = Paquete.objects.get(pk=paquete_id)
        fechas = obtener_fechas_bloqueadas(paquete)
        fechas_optim = optimizar_rangos_bloqueados(fechas, paquete.duracion_dias)
        return JsonResponse({'bloqueadas': fechas_optim})
    except Paquete.DoesNotExist:
        return JsonResponse({'error': 'Paquete no encontrado.'}, status=404)
