from django import template
import json

register = template.Library()

@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, '')

@register.filter
def get_objeto_json(objeto, campos):
    data = {campo: getattr(objeto, campo) for campo in campos}
    return json.dumps(data)

@register.filter
def attr(obj, attr_name):
    """Accede dinámicamente a un atributo del objeto."""
    return getattr(obj, attr_name, '')