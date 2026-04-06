"""
Middleware personalizado para configurar políticas de seguridad
"""


class CSPMiddleware:
    """
    Agrega headers de Content Security Policy para permitir reCAPTCHA y otros recursos externos seguros.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Configurar Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' "
            "https://www.google.com/recaptcha/ "
            "https://www.gstatic.com/ "
            "https://cdn.jsdelivr.net "
            "https://cdnjs.cloudflare.com "
            "https://fonts.googleapis.com "
            "https://widget.complianz.io "
            "https://*.complianz.io; "
            "frame-src 'self' "
            "https://www.google.com/recaptcha/ "
            "https://recaptcha.google.com/ "
            "https://www.google.com/maps "
            "https://maps.google.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net "
            "https://cdnjs.cloudflare.com "
            "https://fonts.googleapis.com "
            "https://widget.complianz.io; "
            "font-src 'self' "
            "https://fonts.gstatic.com "
            "https://cdn.jsdelivr.net "
            "https://cdnjs.cloudflare.com; "
            "connect-src 'self' "
            "https://www.google.com/recaptcha/ "
            "https://www.gstatic.com "
            "https://cmp.complianz.io "
            "https://api-colombia.com; "
            "img-src 'self' https: data:; "
            "media-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'self'"
        )

        return response
