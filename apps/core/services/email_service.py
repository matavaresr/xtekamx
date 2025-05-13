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
            to=[destinatario, remitente]
        )
        correo.attach_alternative(mensaje_html, "text/html")
        correo.send()

    except Exception as e:
        # Puedes loguear o manejar errores aquí
        print(f"[ERROR] No se pudo enviar el correo: {e}")

def enviar_correo_reservacion(destinatario, contexto_html):
    remitente = settings.DEFAULT_FROM_EMAIL
    asunto = f"Reservación en revisión: {contexto_html.get('paquete_nombre')}"

    try:
        mensaje_texto = (
            f"Hola {contexto_html.get('nombre_cliente')},\n\n"
            f"Tu reservación para el paquete '{contexto_html.get('paquete_nombre')}' ha sido registrada.\n"
            f"Está actualmente en revisión y nos pondremos en contacto contigo pronto.\n\n"
            f"Fechas: {contexto_html.get('fecha_inicio')} - {contexto_html.get('fecha_fin')}\n"
            f"Adultos: {contexto_html.get('cantidad_adultos')} | Niños: {contexto_html.get('cantidad_ninos')}\n"
            f"Total: ${contexto_html.get('total_pago')} MXN\n\n"
            "Gracias por reservar con Xteka Huasteca."
        )

        mensaje_html = render_to_string('emails/correo_reservacion.html', contexto_html)

        correo = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=remitente,
            to=[destinatario]
        )
        correo.attach_alternative(mensaje_html, "text/html")
        correo.send()

    except Exception as e:
        print(f"[ERROR] No se pudo enviar el correo de reservación: {e}")

def enviar_correo_aprobacion(destinatario, contexto_html):
    remitente = settings.DEFAULT_FROM_EMAIL
    asunto = f"¡Reservación aprobada! - {contexto_html.get('paquete_nombre')}"

    try:
        mensaje_texto = (
            f"Hola {contexto_html.get('nombre_cliente')},\n\n"
            f"Tu reservación para el paquete '{contexto_html.get('paquete_nombre')}' ha sido aprobada.\n\n"
            f"Fechas: {contexto_html.get('fecha_inicio')} - {contexto_html.get('fecha_fin')}\n"
            f"Adultos: {contexto_html.get('cantidad_adultos')} | Niños: {contexto_html.get('cantidad_ninos')}\n"
            f"Total pagado: ${contexto_html.get('total_pago')} MXN\n\n"
            "¡Gracias por reservar con Xteka Huasteca!"
        )

        mensaje_html = render_to_string('emails/correo_confirmacion.html', contexto_html)

        correo = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=remitente,
            to=[destinatario]
        )
        correo.attach_alternative(mensaje_html, "text/html")
        correo.send()

    except Exception as e:
        print(f"[ERROR] No se pudo enviar el correo de aprobación: {e}")

def enviar_correo_cancelacion(destinatario, contexto_html):
    remitente = settings.DEFAULT_FROM_EMAIL
    asunto = f"Reservación cancelada - {contexto_html.get('paquete_nombre')}"

    try:
        mensaje_texto = (
            f"Hola {contexto_html.get('nombre_cliente')},\n\n"
            f"Lamentamos informarte que tu reservación para el paquete '{contexto_html.get('paquete_nombre')}' ha sido cancelada.\n\n"
            f"Fechas: {contexto_html.get('fecha_inicio')} - {contexto_html.get('fecha_fin')}\n"
            f"Adultos: {contexto_html.get('cantidad_adultos')} | Niños: {contexto_html.get('cantidad_ninos')}\n"
            f"Total previsto: ${contexto_html.get('total_pago')} MXN\n\n"
            "Si tienes dudas o necesitas asistencia, no dudes en contactarnos."
        )

        mensaje_html = render_to_string('emails/correo_cancelacion.html', contexto_html)

        correo = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=remitente,
            to=[destinatario]
        )
        correo.attach_alternative(mensaje_html, "text/html")
        correo.send()

    except Exception as e:
        print(f"[ERROR] No se pudo enviar el correo de cancelación: {e}")
