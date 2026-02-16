from django.contrib.auth import get_user_model

LABELS = {
    'username': 'Usuario',
    'documento': 'Documento',
    'email': 'Correo',
    'first_name': 'Nombre',
    'last_name': 'Apellido',
    'nombre': 'Nombre',
    'apellido': 'Apellido',
    'telefono': 'Telefono',
    'direccion': 'Direccion',
    'fecha_nacimiento': 'Fecha de nacimiento',
    'foto_perfil': 'Foto de perfil',
    'password1': 'Contrasena',
    'password2': 'Confirmar contrasena',
}

FIELD_TAGS = {
    'username': 'field-username',
    'documento': 'field-documento',
    'email': 'field-email',
    'password1': 'field-password',
    'password2': 'field-password',
}

ERROR_CODE_MESSAGES = {
    'required': '{label} es obligatorio.',
    'invalid': '{label} no es valido.',
    'password_mismatch': 'Las contrasenas no coinciden.',
}


def _label_for(field):
    return LABELS.get(field, 'Este campo')


def _tag_for(field):
    return FIELD_TAGS.get(field, 'field-general')


def build_form_messages(form):
    messages = []
    seen = set()
    errors = form.errors.as_data()
    for field, errs in errors.items():
        for err in errs:
            code = getattr(err, 'code', None)
            label = _label_for(field)
            template = ERROR_CODE_MESSAGES.get(code)
            if template:
                text = template.format(label=label)
            else:
                text = err.message
            key = (field, text)
            if key in seen:
                continue
            seen.add(key)
            tags = f"level-error {_tag_for(field)}"
            messages.append({'text': text, 'tags': tags})
    return messages


def build_login_message(form, usuario_o_documento=None):
    errors = form.errors.as_data()
    non_field = errors.get('__all__') or []
    for err in non_field:
        if getattr(err, 'code', None) == 'inactive':
            return {
                'text': 'Tu cuenta esta inactiva, contacta al administrador.',
                'tags': 'level-error field-general'
            }
    if usuario_o_documento:
        User = get_user_model()
        if usuario_o_documento.isdigit() and len(usuario_o_documento) == 10:
            exists = User.objects.filter(documento=usuario_o_documento).exists()
        else:
            exists = User.objects.filter(username=usuario_o_documento).exists()
        if exists:
            return {
                'text': 'Contrasena incorrecta.',
                'tags': 'level-error field-password'
            }
    return {
        'text': 'Usuario o documento incorrecto.',
        'tags': 'level-error field-username'
    }

