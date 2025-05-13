import json
from datetime import datetime, timedelta, date

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.forms import modelform_factory
from django.core.exceptions import ValidationError

import cloudinary
import cloudinary.uploader
import cloudinary.api

from django.db.models import Prefetch
from .forms import LoginForm, PaqueteForm, PaqueteActividadForm
from apps.core.models import (
    Usuario, Cliente, Paquete, Actividad, Reservacion,
    Amenidad, Hotel, TipoPaquete, Ubicacion, ClienteReservacion,
    PaqueteActividad, PaqueteAmenidad, PaqueteUbicacion, ImagenPaquete,
    Faq, Itinerario
)

from apps.core.services.email_service import (
    enviar_correo_reservacion,
    enviar_correo_aprobacion,
    enviar_correo_cancelacion,
)


# Create your views here.
def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
        
    hoy = date.today()
    hace_7_dias = datetime.combine(hoy - timedelta(days=6), datetime.min.time())

    total_reservas = Reservacion.objects.count()
    en_espera = Reservacion.objects.filter(estado=1).count()
    aprobadas = Reservacion.objects.filter(estado=2).count()
    canceladas = Reservacion.objects.filter(estado=3).count()

    ingreso_total = Reservacion.objects.filter(estado=2).aggregate(Sum('total_pago'))['total_pago__sum'] or 0

    ventas_por_dia_qs = (
        Reservacion.objects
        .filter(created_at__gte=hace_7_dias, estado=2)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Count('id'), ingreso=Sum('total_pago'))
        .order_by('day')
    )

    data_dict = {r['day']: r for r in ventas_por_dia_qs}
    fechas = []
    ventas_por_dia = []
    ingresos_por_dia = []

    for i in range(6, -1, -1):
        fecha_actual = hoy - timedelta(days=i)
        dia_semana = (fecha_actual.weekday() + 1) % 7  # 0 = Domingo, 6 = Sábado
        fechas.append(dia_semana)
        datos = data_dict.get(fecha_actual)
        ventas_por_dia.append(datos['total'] if datos else 0)
        ingresos_por_dia.append(float(datos['ingreso']) if datos else 0.0)



    context = {
        'total_reservas': total_reservas,
        'en_espera': en_espera,
        'aprobadas': aprobadas,
        'canceladas': canceladas,
        'ingreso_total': ingreso_total,
        'fechas': fechas, 
        'ventas_por_dia': ventas_por_dia,
        'ingresos_por_dia': ingresos_por_dia,
        'data_random':ventas_por_dia_qs
    }
    return render(request, 'admin_panel/index.html', context)

def login(request):
    
    user_id = request.session.get('user_id')
    usuario_actual = None
    if user_id:
        try:
            usuario_actual = Usuario.objects.get(id=user_id)    
        except Usuario.DoesNotExist:
            usuario_actual = None
    if usuario_actual:
        return redirect('dashboard')    

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data.get('usuario')
            contrasena = form.cleaned_data.get('contrasena')

            try:
                user = Usuario.objects.get(usuario=usuario)
                if contrasena == user.contrasena:
                    request.session['user_id'] = user.id  # Autenticación simple
                    return redirect('dashboard')  # o donde quieras enviarlo
                else:
                    form.add_error('contrasena', 'Contraseña incorrecta')
            except Usuario.DoesNotExist:
                form.add_error('usuario', 'Usuario no encontrado')
    else:
        form = LoginForm()
    return render(request, 'admin_panel/login.html', {'form': form})

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def logout_view(request):
    request.session.flush() 
    return redirect('inicio') 

def crud(request, modelo):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login') 

    modelos = {
        'usuarios': Usuario,
        'clientes': Cliente,
        'paquetes': Paquete,
        'actividades': Actividad,
        'reservaciones': Reservacion,
        'actividad': Actividad,
        'amenidad': Amenidad,
        'hotel': Hotel,
        'ubicacion': Ubicacion,
        'tipopaquete': TipoPaquete,
    }

    user_id = request.session.get('user_id')
    usuario_actual = Usuario.objects.filter(id=user_id).first()

    if modelo not in modelos:
        return render(request, '404.html')

    modelo_clase = modelos[modelo]

    # Carga optimizada
    objetos = modelo_clase.objects.all().order_by('-created_at')

    # Si es reservaciones, optimizamos la carga del cliente
    if modelo == 'reservaciones':
        campos = [campo.name for campo in modelo_clase._meta.fields if campo.name not in ('created_at', 'updated_at', 'id', 'paquete')]
        campos.append('email_cliente')
        campos.insert(0, 'nombre_paquete')

        # Prefetch del cliente desde tabla intermedia
        objetos = objetos.prefetch_related(
            Prefetch(
                'clientereservacion_set',
                queryset=ClienteReservacion.objects.select_related('cliente'),
                to_attr='cliente_reservacion_cached'
            )
        )

        # Inyectamos email del cliente cacheado
        for reservacion in objetos:
            if reservacion.cliente_reservacion_cached:
                cliente = reservacion.cliente_reservacion_cached[0].cliente
                reservacion.email_cliente = cliente.email
                reservacion.nombre_paquete = reservacion.paquete.nombre 
            else:
                reservacion.email_cliente = 'No asignado'    
    else:
        campos = [campo.name for campo in modelo_clase._meta.fields if campo.name not in ('created_at', 'updated_at', 'id')]

    tipo_choices = []
    if 'tipo' in [campo.name for campo in modelo_clase._meta.fields]:
        tipo_field = modelo_clase._meta.get_field('tipo')
        if hasattr(tipo_field, 'choices'):
            tipo_choices = tipo_field.choices

    objetos_count = objetos.count()

    # Paginación
    paginator = Paginator(objetos, 10)
    page = request.GET.get('page')
    try:
        objetos_paginated = paginator.page(page)
    except PageNotAnInteger:
        objetos_paginated = paginator.page(1)
    except EmptyPage:
        objetos_paginated = paginator.page(paginator.num_pages)

    # Respuesta AJAX para la tabla
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('admin_panel/includes/tabla_contenido.html', {
            'objetos': objetos_paginated,
            'columnas': campos,
        })
        return JsonResponse({
            'html': html,
            'page': objetos_paginated.number,
            'total': paginator.num_pages,
        })

    # Render completo
    contexto = {
        'modelo': modelo,
        'columnas': campos,
        'objetos': objetos_paginated,
        'crear_url': f'crud_{modelo}_crear',
        'editar_url': f'crud_{modelo}_editar',
        'eliminar_url': f'crud_{modelo}_eliminar',
        'titulo': modelo.capitalize(),
        'page_obj': objetos_paginated,
        'tipo_choices': tipo_choices,
        'usuario_actual': usuario_actual,
        'objetos_count': objetos_count,
    }

    return render(request, 'admin_panel/crud.html', contexto)


# Eliminar 
def crud_eliminar(request, modelo, pk):
    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    modelos = {
        'usuarios': Usuario,
        'clientes': Cliente,
        'paquetes': Paquete,
        'actividades': Actividad,
        'reservaciones': Reservacion,
        'actividad': Actividad,
        'amenidad': Amenidad,
        'hotel': Hotel,
        'ubicacion': Ubicacion,
        'tipopaquete': TipoPaquete,
    }

    if modelo not in modelos:
        return JsonResponse({'error': 'Modelo inválido'}, status=400)

    modelo_clase = modelos[modelo]
    try:
        objeto = modelo_clase.objects.get(pk=pk)
        objeto.delete()
        return JsonResponse({'success': True})
    except modelo_clase.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)

def crud_crear(request, modelo):
    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    modelos = {
        'usuarios': Usuario,
        'clientes': Cliente,
        'paquetes': Paquete,
        'actividades': Actividad,
        'reservaciones': Reservacion,
        'actividad': Actividad,
        'amenidad': Amenidad,
        'hotel': Hotel,
        'ubicacion': Ubicacion,
        'tipopaquete': TipoPaquete,
    }

    if modelo not in modelos:
        return JsonResponse({'error': 'Modelo inválido'}, status=400)

    modelo_clase = modelos[modelo]

    try:
        data = json.loads(request.body)
        objeto = modelo_clase(**data)
        objeto.full_clean()  # ✅ Ejecutar validaciones del modelo
        objeto.save()
        return JsonResponse({'success': True})

    except ValidationError as e:
        # Devuelve los errores en formato legible para el frontend
        return JsonResponse({'success': False, 'errors': e.message_dict}, status=400)

    except Exception as e:
        # Captura otros errores inesperados (como campos mal escritos)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Editar
def crud_editar(request, modelo, pk):
    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    modelos = {
        'usuarios': Usuario,
        'clientes': Cliente,
        'paquetes': Paquete,
        'actividades': Actividad,
        'reservaciones': Reservacion,
        'actividad': Actividad,
        'amenidad': Amenidad,
        'hotel': Hotel,
        'ubicacion': Ubicacion,
        'tipopaquete': TipoPaquete,
    }

    if modelo not in modelos:
        return JsonResponse({'error': 'Modelo inválido'}, status=400)

    modelo_clase = modelos[modelo]

    try:
        objeto = modelo_clase.objects.get(pk=pk)
        data = json.loads(request.body)

        for key, value in data.items():
            setattr(objeto, key, value)
        objeto.save()

        # Lógica especial para reservaciones
        if modelo == "reservaciones":
            estado = int(data.get("estado"))

            try:
                cliente_relacion = ClienteReservacion.objects.get(reservacion=objeto)
                cliente = cliente_relacion.cliente
            except ClienteReservacion.DoesNotExist:
                return JsonResponse({'error': 'No hay cliente vinculado a esta reservación'}, status=400)

            paquete = objeto.paquete

            contexto = {
                "nombre_cliente": f"{cliente.nombre} {cliente.apellido}",
                "paquete_nombre": paquete.nombre,
                "fecha_inicio": objeto.fecha_inicio.strftime('%d/%m/%Y'),
                "fecha_fin": objeto.fecha_fin.strftime('%d/%m/%Y'),
                "cantidad_adultos": objeto.cantidad_adultos,
                "cantidad_ninos": objeto.cantidad_ninos,
                "total_pago": float(objeto.total_pago),
            }

            if estado == 1:
                enviar_correo_reservacion(cliente.email, contexto)
            elif estado == 2:
                enviar_correo_aprobacion(cliente.email, contexto)
            elif estado == 3:
                enviar_correo_cancelacion(cliente.email, contexto)

        return JsonResponse({'success': True})

    except modelo_clase.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)
 
# CRUD Paquetes
def paquetes_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login') 

    paquetes = Paquete.objects.all()
    hoteles = Hotel.objects.all()
    tipos_paquete = TipoPaquete.objects.all()
    return render(request, 'admin_panel/paquetes.html', {
        'paquetes': paquetes,
        'hoteles': hoteles,
        'tipos_paquete': tipos_paquete
    })

def crear_paquete(request):
    if request.method == 'POST':
        form = PaqueteForm(request.POST, request.FILES)
        if form.is_valid():
            paquete = form.save()
            return JsonResponse({'id': paquete.id})
        else:
            # Transformar errores a lista plana por campo
            error_dict = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({'errors': error_dict}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def eliminar_paquete(request, paquete_id):
    if request.method == 'POST':
        try:
            paquete = Paquete.objects.get(id=paquete_id)
            paquete.delete()
            return JsonResponse({'success': True})
        except Paquete.DoesNotExist:
            return JsonResponse({'error': 'Paquete no encontrado'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def paquete_detalle(request, paquete_id):
    paquete = Paquete.objects.get(pk=paquete_id)
    actividades = Actividad.objects.all()
    amenidades = Amenidad.objects.all()
    ubicaciones = Ubicacion.objects.all()
    
    actividades_seleccionadas = PaqueteActividad.objects.filter(paquete=paquete).values_list('actividad_id', flat=True)
    seleccionadas_amenidades = set(paquete.paqueteamenidad_set.values_list('amenidad_id', flat=True))
    seleccionadas_ubicaciones = set(paquete.paqueteubicacion_set.values_list('ubicacion_id', flat=True))
    
        # Obtener imágenes asociadas al paquete
    imagenes = ImagenPaquete.objects.filter(paquete=paquete).values(
        'id', 'url_imagen', 'descripcion', 'es_portada'
    )

    datos = {
        'paquete': {
            'id': paquete.id,
            'nombre': paquete.nombre,
            'descripcion': paquete.descripcion,
            'duracion_dias': paquete.duracion_dias,
            'precio_adulto': float(paquete.precio_adulto),
            'precio_nino': float(paquete.precio_nino),
            'minimo_personas': paquete.minimo_personas,
            'maximo_personas': paquete.maximo_personas,
            'hotel': paquete.hotel.nombre if paquete.hotel else '',
            'tipo_paquete': paquete.tipo_paquete.nombre if paquete.tipo_paquete else ''
        },
        'actividades': [
            {'id': a.id, 'nombre': a.nombre, 'seleccionada': a.id in actividades_seleccionadas}
            for a in actividades
        ],
        "amenidades": [
            {"id": a.id, "nombre": a.nombre, "seleccionada": a.id in seleccionadas_amenidades}
            for a in amenidades
        ],
        "ubicaciones": [
            {"id": a.id, "nombre": a.nombre, "seleccionada": a.id in seleccionadas_ubicaciones}
            for a in ubicaciones    
        ],
        "imagenes": list(imagenes) 
    }
    return JsonResponse(datos)

@csrf_exempt
def guardar_actividades_paquete(request, paquete_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        actividades_ids = data.get('actividades', [])

        try:
            paquete = Paquete.objects.get(pk=paquete_id)
        except Paquete.DoesNotExist:
            return JsonResponse({'error': 'Paquete no encontrado'}, status=404)

        # Eliminar actividades existentes
        PaqueteActividad.objects.filter(paquete=paquete).delete()

        # Asociar nuevas actividades
        for actividad_id in actividades_ids:
            actividad = Actividad.objects.get(pk=actividad_id)
            PaqueteActividad.objects.create(paquete=paquete, actividad=actividad)

        return JsonResponse({'message': 'Actividades guardadas correctamente'})
    
@csrf_exempt
def guardar_amenidades_paquete(request, paquete_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        amenidades_ids = data.get('amenidades', [])

        try:
            paquete = Paquete.objects.get(pk=paquete_id)
        except Paquete.DoesNotExist:
            return JsonResponse({'error': 'Paquete no encontrado'}, status=404)

        # Eliminar amenidad existentes
        PaqueteAmenidad.objects.filter(paquete=paquete).delete()

        # Asociar nuevas aamenidades
        for amenidad_id in amenidades_ids:
            amenidad = Amenidad.objects.get(pk=amenidad_id)
            PaqueteAmenidad.objects.create(paquete=paquete, amenidad=amenidad, estado=1)

        return JsonResponse({'message': 'Amenidades guardadas correctamente'})
    
@csrf_exempt
def guardar_ubicaciones_paquete(request, paquete_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        ubicaciones_ids = data.get('ubicaciones', [])

        try:
            paquete = Paquete.objects.get(pk=paquete_id)
        except Paquete.DoesNotExist:
            return JsonResponse({'error': 'Paquete no encontrado'}, status=404)

        # Eliminar ubicaciones existentes
        PaqueteUbicacion.objects.filter(paquete=paquete).delete()

        # Asociar nuevas ubicaciones
        for ubicacion_id in ubicaciones_ids:
            ubicacion = Ubicacion.objects.get(pk=ubicacion_id)
            PaqueteUbicacion.objects.create(paquete=paquete, ubicacion=ubicacion)

        return JsonResponse({'message': 'Amenidades guardadas correctamente'})

@csrf_exempt
def subir_imagen(request):
    if request.method == 'POST':
        archivo = request.FILES['file']
        titulo = request.POST.get('titulo', 'sin_titulo')
        subida = cloudinary.uploader.upload(archivo, folder="banco/")
        return JsonResponse({'url': subida['secure_url'], 'public_id': subida['public_id'], 'titulo': titulo})

@csrf_exempt
def eliminar_imagen(request):
    if request.method == 'POST':
        public_id = request.POST.get('public_id')
        cloudinary.uploader.destroy(public_id)
        return JsonResponse({'status': 'ok'})
    
@csrf_exempt
def reemplazar_imagen(request):
    if request.method == 'POST':
        public_id = request.POST.get('public_id')
        nuevo_archivo = request.FILES['file']
        cloudinary.uploader.destroy(public_id)
        subida = cloudinary.uploader.upload(nuevo_archivo, folder="banco/")
        return JsonResponse({'url': subida['secure_url'], 'public_id': subida['public_id']})

def listar_imagenes(request):
     cursor = request.GET.get("cursor", None)
 
     params = {
         "type": "upload",
         "prefix": "banco/",  # Ajusta si usas otro folder
         "max_results": 12,
     }
 
     if cursor:
         params["next_cursor"] = cursor
 
     try:
         response = cloudinary.api.resources(**params)
         return JsonResponse({
             "resources": [
                 {
                     "url": img["secure_url"],
                     "public_id": img["public_id"]
                 } for img in response["resources"]
             ],
             "next_cursor": response.get("next_cursor")
         })
     except Exception as e:
         return JsonResponse({"error": str(e)}, status=500)
     
@require_POST
def guardar_imagen_paquete(request):
    url_imagen = request.POST.get('url_imagen')
    paquete_id = request.POST.get('paquete_id')

    if not (url_imagen and paquete_id):
        return JsonResponse({'error': 'Faltan datos'}, status=400)

    try:
        paquete = Paquete.objects.get(id=paquete_id)
        imagen = ImagenPaquete.objects.create(paquete=paquete, url_imagen=url_imagen)
        return JsonResponse({
            'id': imagen.id,
            'url_imagen': imagen.url_imagen,
            'descripcion': imagen.descripcion,
            'es_portada': imagen.es_portada
        })
    except Paquete.DoesNotExist:
        return JsonResponse({'error': 'Paquete no encontrado'}, status=404)
    

def obtener_imagenes_paquete(request, paquete_id):
    imagenes = ImagenPaquete.objects.filter(paquete_id=paquete_id)
    data = [{
        'id': img.id,
        'url_imagen': img.url_imagen,
        'descripcion': img.descripcion,
        'es_portada': img.es_portada,
    } for img in imagenes]
    return JsonResponse(data, safe=False)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def eliminar_imagen_paquete(request, imagen_id):
    if request.method == 'DELETE':
        try:
            ImagenPaquete.objects.get(id=imagen_id).delete()
            return HttpResponse(status=204)
        except ImagenPaquete.DoesNotExist:
            return HttpResponse(status=404)
    return HttpResponse(status=405)

@csrf_exempt
def actualizar_portada(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        imagen_id = data.get('imagen_id')
        paquete_id = data.get('paquete_id')

        # Desmarcar todas las demás como portada
        ImagenPaquete.objects.filter(paquete_id=paquete_id).update(es_portada=False)

        # Marcar esta imagen como portada
        ImagenPaquete.objects.filter(id=imagen_id).update(es_portada=True)

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def guardar_faq(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        paquete_id = data.get('paquete_id')
        pregunta = data.get('pregunta')
        respuesta = data.get('respuesta')

        if not (paquete_id and pregunta and respuesta):
            return JsonResponse({'success': False, 'error': 'Datos incompletos'})

        try:
            paquete = Paquete.objects.get(id=paquete_id)
            faq = Faq.objects.create(paquete=paquete, pregunta=pregunta, respuesta=respuesta)
            return JsonResponse({'success': True, 'faq_id': faq.id})
        except Paquete.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Paquete no encontrado'})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def listar_faqs(request):
    paquete_id = request.GET.get('paquete_id')
    faqs = Faq.objects.filter(paquete_id=paquete_id).values('id', 'pregunta', 'respuesta')
    return JsonResponse({'faqs': list(faqs)})

@csrf_exempt
@require_http_methods(["DELETE"])
def eliminar_faq(request, faq_id):
    try:
        faq = Faq.objects.get(id=faq_id)
        faq.delete()
        return JsonResponse({'success': True})
    except Faq.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'FAQ no encontrada'})
    
@require_POST
def guardar_itinerario(request):
    data = json.loads(request.body)
    paquete_id = data.get('paquete_id')
    titulo = data.get('titulo')
    dia = data.get('dia')
    descripcion = data.get('descripcion')

    # Validar si ya hay un itinerario con ese día
    if Itinerario.objects.filter(paquete_id=paquete_id, dia=dia).exists():
        return JsonResponse({'success': False, 'error': 'DIA_REPETIDO'})

    Itinerario.objects.create(
        paquete_id=paquete_id,
        titulo=titulo,
        dia=dia,
        descripcion=descripcion
    )
    return JsonResponse({'success': True})

def listar_itinerarios(request):
    paquete_id = request.GET.get('paquete_id')
    itinerarios = Itinerario.objects.filter(paquete_id=paquete_id).order_by('dia')

    # Obtener duración del paquete
    try:
        paquete = Paquete.objects.get(id=paquete_id)
        duracion = paquete.duracion_dias
    except Paquete.DoesNotExist:
        return JsonResponse({'error': 'Paquete no encontrado'}, status=404)

    data = {
        'itinerarios': [
            {'id': i.id, 'dia': i.dia, 'descripcion': i.descripcion}
            for i in itinerarios
        ],
        'paquete': {
            'duracion_dias': duracion
        }
    }
    return JsonResponse(data)

@require_http_methods(["DELETE"])
def eliminar_itinerario(request, itinerario_id):
    try:
        itinerario = Itinerario.objects.get(id=itinerario_id)
        itinerario.delete()
        return JsonResponse({'success': True})
    except Itinerario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'NO_EXISTE'})