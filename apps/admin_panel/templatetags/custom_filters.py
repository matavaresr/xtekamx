import json
from decimal import Decimal
from datetime import date, datetime
from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model

register = template.Library()

@register.filter
def get_attr(objeto, attr):
    valor = getattr(objeto, attr, None)

    if callable(valor):
        valor = valor()

    if hasattr(valor, '__str__') and not isinstance(valor, (int, float, str, bool, type(None))):
        return str(valor)

    return valor

@register.filter
def get_objeto_json(objeto, campos):
    campo_list = campos.split(',')
    data = {}

    for campo in campo_list:
        valor = getattr(objeto, campo, None)

        if callable(valor):
            valor = valor()

        if isinstance(valor, Model):
            # Es una relación, usamos su representación de cadena
            valor = str(valor)

        data[campo] = str(valor) if valor is not None else ''

    return json.dumps(data)

@register.filter
def attr(obj, attr_name):
    """Accede dinámicamente a un atributo del objeto."""
    return getattr(obj, attr_name, '')

@register.filter
def get_field_value(obj, field_name):
    return getattr(obj, field_name, '')