from django.shortcuts import render

# Página principal
def home(request):
    return render(request, 'customers/index.html')

# Página de contacto
def contacto(request):
    return render(request, 'customers/contacto.html')

# Página de cómo llegar
def como_llegar(request):
    return render(request, 'customers/como_llegar.html')

# Página acerca de
def acerca_de(request):
    return render(request, 'customers/acerca_de.html')

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