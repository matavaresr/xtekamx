from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

def enviar_correo_contacto(destinatario, asunto, mensaje_texto, mensaje_html_context):
    remitente = settings.DEFAULT_FROM_EMAIL

    try:
        # Renderiza plantilla HTML
        mensaje_html = render_to_string('emails/correo_contacto.html', mensaje_html_context)

        correo = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=remitente,
            to=[destinatario]
        )
        correo.attach_alternative(mensaje_html, "text/html")
        correo.send()

    except Exception as e:
        # Puedes loguear o manejar errores aquí
        print(f"[ERROR] No se pudo enviar el correo: {e}")
