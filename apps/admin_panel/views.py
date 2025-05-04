import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.forms import modelform_factory
from .forms import LoginForm
from django.contrib.auth import login, authenticate
from django.apps import apps
from apps.core.models import Usuario,Cliente, Paquete, Actividad, Reservacion
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def dashboard(request):
    return render(request, 'admin_panel/index.html')

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
    modelos = {
        'usuarios': Usuario,
        'clientes': Cliente,
        'paquetes': Paquete,
        'actividades': Actividad,
        'reservaciones': Reservacion,
    }
    
    user_id = request.session.get('user_id')
    usuario_actual = None
    if user_id:
        usuario_actual = Usuario.objects.get(id=user_id)    

    if modelo not in modelos:
        return render(request, '404.html')

    modelo_clase = modelos[modelo]
    objetos = modelo_clase.objects.all().order_by('-created_at')  # Ajusta el orden si lo deseas
    
    objetos_count = objetos.count()

    tipo_choices = []
    if 'tipo' in [campo.name for campo in modelo_clase._meta.fields]:
        tipo_field = modelo_clase._meta.get_field('tipo')
        if hasattr(tipo_field, 'choices'):
            tipo_choices = tipo_field.choices  # Obtener las opciones de 'choices'
        
    # Obtener los campos del modelo (excepto 'id', 'created_at' y 'updated_at')
    campos = [campo.name for campo in modelo_clase._meta.fields if campo.name not in ('created_at', 'updated_at', 'id')]

    # Configuración de la paginación
    paginator = Paginator(objetos, 10)  # 10 objetos por página
    page = request.GET.get('page')

    try:
        objetos_paginated = paginator.page(page)
    except PageNotAnInteger:
        objetos_paginated = paginator.page(1)  # Si no es un número de página válido, mostrar la primera página
    except EmptyPage:
        objetos_paginated = paginator.page(paginator.num_pages)  # Si la página está fuera del rango, mostrar la última página

    # Verificar si la solicitud es AJAX usando el encabezado 'X-Requested-With'
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('admin_panel/includes/tabla_contenido.html', {
            'objetos': objetos_paginated,
            'columnas': campos,
        })
        return JsonResponse({
            'html': html,
            'page': objetos_paginated.number,
            'total': objetos_paginated.paginator.num_pages,
        })

    # Si no es una solicitud AJAX, renderizamos la página completa
    contexto = {
        'modelo': modelo,
        'columnas': campos,
        'objetos': objetos_paginated,
        'crear_url': f'crud_{modelo}_crear',
        'editar_url': f'crud_{modelo}_editar',
        'eliminar_url': f'crud_{modelo}_eliminar',
        'titulo': modelo.capitalize(),
        'page_obj': objetos_paginated,  # Paginación
        'tipo_choices': tipo_choices,
        'usuario_actual': usuario_actual,
        'objetos_count': objetos_count,  # Contador de objetos
    }

    return render(request, 'admin_panel/crud.html', contexto)



def crud_eliminar(request, modelo, pk):
    if request.method == "POST":
        modelos = {
            'usuarios': Usuario,
            'clientes': Cliente,
            'paquetes': Paquete,
            'actividades': Actividad,
            'reservaciones': Reservacion,
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
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def crud_crear(request, modelo):
    if request.method == "POST":
        modelos = {
            'usuarios': Usuario,
            'clientes': Cliente,
            'paquetes': Paquete,
            'actividades': Actividad,
            'reservaciones': Reservacion,
        }
        if modelo not in modelos:
            return JsonResponse({'error': 'Modelo inválido'}, status=400)

        modelo_clase = modelos[modelo]
        data = json.loads(request.body)
        objeto = modelo_clase.objects.create(**data)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def crud_editar(request, modelo, pk):
    if request.method == "POST":
        modelos = {
            'usuarios': Usuario,
            'clientes': Cliente,
            'paquetes': Paquete,
            'actividades': Actividad,
            'reservaciones': Reservacion,
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
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

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
