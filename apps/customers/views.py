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

from .forms import CustomUserCreationForm

from apps.core.services.email_service import enviar_correo_reservacion

from apps.core.models import (
    Actividad, Paquete, ImagenPaquete, TipoPaquete,
    Cliente, Reservacion, ClienteReservacion, Amenidad, Ubicacion
)


# Página principal
def home(request):
    testimonios = [
        {
            "titulo": "Excelente experiencia",
            "descripcion": "Quiero agradecer a mis amigos de Xteka.mx por invitarme a esta aventura. Disfruté mucho de todas las atracciones, actividades y servicios que me brindaron. Les recomiendo visitar la Cascada de El Meco, pues es un lugar para salir un poco de tu zona de confort y desconectarse de todo. ¡Servicio 10/10!",
            "instagram": "@fitnessalvarezz (120,000 seguidores)",
            "ubicacion": "Monterrey, Nuevo León, México",
            "imagen": "https://xteka.mx/wp-content/uploads/2024/12/influencer-1.png.webp"
        },
        {
            "titulo": "Un servicio inigualable",
            "descripcion": "En nuestro viaje por México, paramos en la Huasteca y nos encontramos con Olaff, un guía de Xteka.mx. Nos llevó a realizar actividades en las hermosas aguas color turquesa y a las cascadas, y fue muy atento en todo momento. Nos llevamos buenas tomas y pueden encontrar el video que realizamos en Instagram y TikTok. ¡100% recomendado tomar un tour con ellos!",
            "instagram": "viajando.conlopuesto (128,000 seguidores)",
            "ubicacion": "España",
            "imagen": "https://xteka.mx/wp-content/uploads/2024/12/influencer-2.png.webp"
        },
        {
            "titulo": "Atención espectacular",
            "descripcion": "Amigos, vivan la experiencia de la Huasteca en El Naranjo, San Luis Potosí. Hagan sus recorridos con guías capacitados siempre y recuerden traer su chaleco salvavidas en todo momento. Pero sobre todo, disfruten de estos maravillosos sitios naturales.",
            "instagram": "@aztecasanluispotosi @jorgelopez_perez (6,641 seguidores)",
            "ubicacion": "San Luis Potosí, México",
            "imagen": "https://xteka.mx/wp-content/uploads/2024/12/influencer-3.png.webp"
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

class PaqueteDetailView(DetailView):
    model = Paquete
    template_name = 'customers/paquete_unico.html'
    context_object_name = 'paquete'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paquete = self.get_object()

        # Fechas bloqueadas optimizadas
        rangos_originales = obtener_fechas_bloqueadas(paquete)
        rangos_optim = optimizar_rangos_bloqueados(rangos_originales, paquete.duracion_dias)
        context['fechas_bloqueadas'] = rangos_optim

        # Amenidades activas relacionadas
        context['amenidades'] = Amenidad.objects.filter(
            paqueteamenidad__paquete=paquete,
            paqueteamenidad__estado=1
        )

        # Ubicaciones relacionadas
        context['ubicaciones'] = Ubicacion.objects.filter(
            paqueteubicacion__paquete=paquete
        )

        # Actividades relacionadas
        context['actividades'] = Actividad.objects.filter(
            paqueteactividad__paquete=paquete
        )

        return context


def obtener_fechas_bloqueadas(paquete):
    reservaciones = Reservacion.objects.filter(paquete=paquete)
    return [
        {
            "from": r.fecha_inicio.isoformat(),
            "to": r.fecha_fin.isoformat()
        } for r in reservaciones
    ]


def optimizar_rangos_bloqueados(rangos, duracion_dias):
    if not rangos:
        return []

    # Convertir a objetos datetime ordenados
    parsed = sorted([
        {
            "from": datetime.strptime(r["from"], "%Y-%m-%d"),
            "to": datetime.strptime(r["to"], "%Y-%m-%d")
        }
        for r in rangos
    ], key=lambda r: r["from"])

    resultado = [parsed[0]]

    for actual in parsed[1:]:
        previo = resultado[-1]
        diferencia = (actual["from"] - previo["to"]).days

        if diferencia <= duracion_dias:
            # Unir los rangos
            previo["to"] = max(previo["to"], actual["to"])
        else:
            resultado.append(actual)

    # Convertir a formato JSON serializable
    return [
        {
            "from": r["from"].strftime("%Y-%m-%d"),
            "to": r["to"].strftime("%Y-%m-%d")
        } for r in resultado
    ]


@csrf_exempt
@require_POST
def guardar_reservacion_ajax(request):
    try:
        data = json.loads(request.body)

        required = [
            'nombre', 'apellido', 'email', 'telefono',
            'fecha_inicio', 'cantidad_adultos', 'cantidad_ninos', 'paquete_id'
        ]
        if not all(data.get(campo) for campo in required):
            return JsonResponse({'error': 'Faltan campos obligatorios.'}, status=400)

        paquete = get_object_or_404(Paquete, id=data['paquete_id'])

        fecha_inicio = datetime.strptime(data['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = fecha_inicio + timedelta(days=paquete.duracion_dias - 1)

        # Validar solapamiento de fechas
        conflicto = Reservacion.objects.filter(
            paquete=paquete,
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio
        ).exists()
        if conflicto:
            return JsonResponse({'error': 'Ya existe una reservación en ese rango de fechas para este paquete.'}, status=409)

        usar_previos = data.get('usar_datos_previos')
        cliente_existente = Cliente.objects.filter(email=data['email']).first()

        if cliente_existente:
            if cliente_existente.nombre.strip().lower() == data['nombre'].strip().lower():
                if not usar_previos:
                    return JsonResponse({
                        'match': True,
                        'cliente': {
                            'nombre': cliente_existente.nombre,
                            'apellido': cliente_existente.apellido,
                            'telefono': cliente_existente.telefono
                        }
                    })
                else:
                    cliente = cliente_existente  # usar el existente
            else:
                return JsonResponse({'error': 'Este correo ya está registrado con otro nombre.'}, status=400)
        else:
            # Crear nuevo cliente
            cliente = Cliente.objects.create(
                nombre=data['nombre'],
                apellido=data['apellido'],
                email=data['email'],
                telefono=data['telefono']
            )

        total_pago = (
            paquete.precio_adulto * int(data['cantidad_adultos']) +
            paquete.precio_nino * int(data['cantidad_ninos'])
        )

        reservacion = Reservacion.objects.create(
            paquete=paquete,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            cantidad_adultos=data['cantidad_adultos'],
            cantidad_ninos=data['cantidad_ninos'],
            total_pago=total_pago,
            estado=1  # Estado: En revisión
        )

        ClienteReservacion.objects.create(cliente=cliente, reservacion=reservacion)

        # Enviar correo de confirmación
        enviar_correo_reservacion(cliente.email, {
            'nombre_cliente': cliente.nombre,
            'paquete_nombre': paquete.nombre,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'cantidad_adultos': data['cantidad_adultos'],
            'cantidad_ninos': data['cantidad_ninos'],
            'total_pago': total_pago,
        })

        return JsonResponse({'success': 'Reservación registrada correctamente.'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
