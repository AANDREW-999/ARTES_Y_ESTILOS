from django import template

register = template.Library()

# Cambia 'accesibilidad/widget.html' por 'accesibilidad.html'
@register.inclusion_tag('accesibilidad.html') 
def accesibilidad_widget():
    return {}