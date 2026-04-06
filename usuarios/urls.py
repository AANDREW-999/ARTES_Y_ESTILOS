from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # ========================================
    # 🔐 AUTENTICACIÓN
    # ========================================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('validar-usuario/', views.validar_usuario_documento_view, name='validar_usuario_documento'),
    path('cuenta-inactiva/', views.panel_inactivo_view, name='panel_inactivo'),

    # ========================================
    # 👤 PERFIL DE USUARIO
    # ========================================
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),

    # ========================================
    # 👥 GESTIÓN DE USUARIOS
    # ========================================
    path('usuarios/', views.lista_usuarios_view, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario_view, name='crear_usuario'),
    path('usuarios/<int:user_id>/ver/', views.visualizar_usuario_view, name='visualizar_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario_view, name='editar_usuario'),
    path('usuarios/<int:user_id>/desactivar/', views.desactivar_usuario_view, name='desactivar_usuario'),
    path('usuarios/<int:user_id>/activar/', views.activar_usuario_view, name='activar_usuario'),
    path('usuarios/<int:user_id>/convertir-superadmin/', views.convertir_superadmin_view, name='convertir_superadmin'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario_view, name='eliminar_usuario'),

    # ========================================
    # 🔒 SEGURIDAD
    # ========================================
    path('seguridad/', views.seguridad_view, name='seguridad'),
    path('backup/generar/', views.generar_backup_db_view, name='generar_backup_db'),
    path('backup/restaurar/', views.restaurar_backup_db_view, name='restaurar_backup_db'),
    path('backup/<str:backup_name>/descargar/', views.descargar_backup_db_view, name='descargar_backup_db'),
    path('backup/<str:backup_name>/eliminar/', views.eliminar_backup_db_view, name='eliminar_backup_db'),

    # ========================================
    # 🔧 RECUPERACIÓN DE CONTRASEÑA
    # ========================================
    path('recuperar-password/', views.RecuperarPasswordView.as_view(), name='password_reset'),
    path('recuperar-password/enviado/', views.RecuperarPasswordHechoView.as_view(), name='password_reset_done'),
    path('restablecer-password/<uidb64>/<token>/', views.RestablecerPasswordConfirmarView.as_view(), name='password_reset_confirm'),
    path('restablecer-password/completado/', views.RestablecerPasswordCompletoView.as_view(), name='password_reset_complete'),

    # ========================================
    # 🚫 REGISTRO INTERNO
    # ========================================
    path('__registro_interno__/', views.registro, name='registro'),
]