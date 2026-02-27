from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # ========================================
    # 🔐 AUTENTICACIÓN
    # ========================================
    path('panel/login/', views.login_view, name='login'),
    path('panel/logout/', views.logout_view, name='logout'),

    # ========================================
    # 👤 PERFIL DE USUARIO
    # ========================================
    path('panel/perfil/', views.perfil_view, name='perfil'),
    path('panel/perfil/editar/', views.editar_perfil_view, name='editar_perfil'),

    # ========================================
    # 👥 GESTIÓN DE USUARIOS (SOLO SUPERADMINS)
    # ========================================
    path('panel/usuarios/', views.lista_usuarios_view, name='lista_usuarios'),
    path('panel/usuarios/crear/', views.crear_usuario_view, name='crear_usuario'),
    path('panel/usuarios/<int:user_id>/ver/', views.visualizar_usuario_view, name='visualizar_usuario'),
    path('panel/usuarios/<int:user_id>/editar/', views.editar_usuario_view, name='editar_usuario'),
    path('panel/usuarios/<int:user_id>/desactivar/', views.desactivar_usuario_view, name='desactivar_usuario'),
    path('panel/usuarios/<int:user_id>/activar/', views.activar_usuario_view, name='activar_usuario'),
    path('panel/usuarios/<int:user_id>/eliminar/', views.eliminar_usuario_view, name='eliminar_usuario'),

    # ========================================
    # 🔧 RECUPERACIÓN DE CONTRASEÑA
    # ========================================
    path('panel/recuperar-password/', views.RecuperarPasswordView.as_view(), name='password_reset'),
    path('panel/recuperar-password/enviado/', views.RecuperarPasswordHechoView.as_view(), name='password_reset_done'),
    path('panel/restablecer-password/<uidb64>/<token>/', views.RestablecerPasswordConfirmarView.as_view(), name='password_reset_confirm'),
    path('panel/restablecer-password/completado/', views.RestablecerPasswordCompletoView.as_view(), name='password_reset_complete'),

    # ========================================
    # 🚫 REGISTRO (OCULTO DEL PÚBLICO)
    # ========================================
    path('__registro_interno__/', views.registro, name='registro'),
]
