from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

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

# Vista para iniciar sesión
def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('inicio')  # Redirigir a la página de inicio
    else:
        form = AuthenticationForm()
    return render(request, 'customers/iniciar_sesion.html', {'form': form})

# Vista para crear cuenta
def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('iniciar_sesion')  # Redirigir al login después del registro
    else:
        form = CustomUserCreationForm()
    return render(request, 'customers/registro.html', {'form': form})


# Vista general de paquetes
def paquetes(request):
    # Aquí podrías pasar una lista de paquetes desde la base de datos
    paquetes_list = [
        {"id": 1, "nombre": "Paquete A"},
        {"id": 2, "nombre": "Paquete B"},
        {"id": 3, "nombre": "Paquete C"},
    ]
    return render(request, 'customers/paquetes.html', {'paquetes': paquetes_list})

# Vista de un paquete específico
def paquete_unico(request, id):
    # Aquí podrías obtener el paquete específico desde la base de datos
    paquete = {"id": id, "nombre": f"Paquete {id}"}
    return render(request, 'customers/paquete_unico.html', {'paquete': paquete})

# Página de actividades
def actividades(request):
    # Aquí podrías pasar una lista de actividades desde la base de datos
    actividades_list = [
        {"id": 1, "nombre": "Actividad 1"},
        {"id": 2, "nombre": "Actividad 2"},
        {"id": 3, "nombre": "Actividad 3"},
    ]
    return render(request, 'customers/actividades.html', {'actividades': actividades_list})

# Página acerca de
def terminosycondiciones(request):
    return render(request, 'customers/terminosycondiciones.html')