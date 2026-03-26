"""
Utilidades para sanitizar entrada de usuarios y prevenir XSS.
"""
import bleach
import re


def sanitizar_html(texto, permitir_html=False):
    """
    Sanitiza texto para prevenir ataques XSS.
    
    Args:
        texto (str): Texto a sanitizar
        permitir_html (bool): Si True, permite etiquetas HTML seguras. Si False, las remueve.
    
    Returns:
        str: Texto sanitizado
    """
    if not texto:
        return texto
    
    texto = str(texto).strip()
    
    if permitir_html:
        # Permitir solo etiquetas seguras y atributos seguros
        etiquetas_permitidas = [
            'b', 'i', 'em', 'strong', 'p', 'br', 'a', 'ul', 'ol', 'li',
            'blockquote', 'h2', 'h3', 'h4', 'h5', 'h6'
        ]
        atributos_permitidos = {
            'a': ['href', 'title']
        }
        return bleach.clean(
            texto,
            tags=etiquetas_permitidas,
            attributes=atributos_permitidos,
            strip=True
        )
    else:
        # Remover todas las etiquetas HTML
        return bleach.clean(texto, tags=[], strip=True)


def detectar_codigo_javascript(texto):
    """
    Detecta si el texto contiene patrones de JavaScript malicioso.
    
    Args:
        texto (str): Texto a validar
    
    Returns:
        bool: True si contiene patrones maliciosos, False en caso contrario
    """
    if not texto:
        return False
    
    patrones_maliciosos = [
        r'<script[^>]*>',  # <script>
        r'on\w+\s*=',      # onerror=, onclick=, etc.
        r'javascript:',    # javascript:
        r'data:text/html', # data:text/html
        r'<iframe',        # <iframe>
        r'<embed',         # <embed>
        r'<object',        # <object>
    ]
    
    texto_lower = texto.lower()
    
    for patron in patrones_maliciosos:
        if re.search(patron, texto_lower):
            return True
    
    return False


def validar_y_sanitizar(campo_nombre, texto):
    """
    Valida y sanitiza texto en un campo.
    Lanza excepción si detecta código malicioso, de lo contrario retorna texto sanitizado.
    
    Args:
        campo_nombre (str): Nombre del campo (para mensaje de error)
        texto (str): Texto a validar
    
    Returns:
        str: Texto sanitizado
        
    Raises:
        ValueError: Si se detecta código malicioso
    """
    from django import forms
    
    if not texto:
        return texto
    
    if detectar_codigo_javascript(texto):
        raise forms.ValidationError(
            f"{campo_nombre} contiene código potencialmente malicioso. No se permiten etiquetas HTML/JavaScript."
        )
    
    return sanitizar_html(texto, permitir_html=False)
