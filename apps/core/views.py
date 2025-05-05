from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_POST
from apps.core.services.email_service import enviar_correo_contacto
from django.conf import settings
from django_ratelimit.decorators import ratelimit

@require_POST
@ratelimit(key='ip', rate='5/m', block=True)
def envio_correo_contacto(request):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponseForbidden("Acceso no autorizado")

    name = request.POST.get('name')
    last_name = request.POST.get('last_name')
    telefono = request.POST.get('telefono')
    email = request.POST.get('email')
    mensaje = request.POST.get('mensaje')
    if email and mensaje:
        enviar_correo_contacto(
            destinatario=settings.DEFAULT_FROM_EMAIL,
            asunto="Nuevo mensaje de contacto",
            mensaje_texto=mensaje,
            mensaje_html_context={
                'name': name,
                'last_name': last_name,
                'email': email,
                'telefono': telefono,
                'mensaje': mensaje
            }
        )

        return HttpResponse("OK")
    return HttpResponse("Faltan datos", status=400)