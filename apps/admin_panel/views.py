import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render, redirect,  get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
import cloudinary
import cloudinary.uploader
import cloudinary.api

from .forms import LoginForm, PaqueteForm, PaqueteActividadForm
from apps.core.models import Usuario, Cliente, Paquete, Actividad, Reservacion, Amenidad, Hotel, TipoPaquete, Ubicacion, PaqueteActividad, PaqueteAmenidad, PaqueteUbicacion, ImagenPaquete

# Vista principal del panel
def dashboard(request):
    return render(request, 'admin_panel/index.html')

# Vista de inicio de sesión
def login(request):
    user_id = request.session.get('user_id')
    usuario_actual = Usuario.objects.filter(id=user_id).first()

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
                    request.session['user_id'] = user.id
                    return redirect('dashboard')
                else:
                    form.add_error('contrasena', 'Contraseña incorrecta')
            except Usuario.DoesNotExist:
                form.add_error('usuario', 'Usuario no encontrado')
    else:
        form = LoginForm()
    return render(request, 'admin_panel/login.html', {'form': form})

# Cierre de sesión
def logout_view(request):
    request.session.flush()
    return redirect('inicio')

# CRUD general
def crud(request, modelo):
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
    objetos = modelo_clase.objects.all().order_by('-created_at')
    objetos_count = objetos.count()

    # Obtener campos útiles y choices si existen
    campos = [campo.name for campo in modelo_clase._meta.fields if campo.name not in ('created_at', 'updated_at', 'id')]
    tipo_choices = []
    if 'tipo' in [campo.name for campo in modelo_clase._meta.fields]:
        tipo_field = modelo_clase._meta.get_field('tipo')
        if hasattr(tipo_field, 'choices'):
            tipo_choices = tipo_field.choices

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

    # Renderizado completo
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

# Crear
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
    data = json.loads(request.body)
    objeto = modelo_clase.objects.create(**data)
    return JsonResponse({'success': True})

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

        return JsonResponse({'success': True})
    except modelo_clase.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)

 
# CRUD Paquetes
def paquetes_list(request):
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
            return JsonResponse({'id': paquete.id})  # Devuelve el ID del paquete
        else:
            return JsonResponse({'errors': form.errors}, status=400)
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