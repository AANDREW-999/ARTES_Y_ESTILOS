from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # Recuperación de password (paths en español)
    path('recuperar-password/', views.RecuperarPasswordView.as_view(), name='password_reset'),
    path('recuperar-password/enviado/', views.RecuperarPasswordHechoView.as_view(), name='password_reset_done'),
    path('restablecer-password/<uidb64>/<token>/', views.RestablecerPasswordConfirmarView.as_view(), name='password_reset_confirm'),
    path('restablecer-password/completado/', views.RestablecerPasswordCompletoView.as_view(), name='password_reset_complete'),

    # Perfil de usuario
    path('perfil/', views.perfil, name='perfil'),

    # Panel de administración (placeholders si aún no están implementadas)
    path('usuarios/', views.lista_usuarios_view, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario_view, name='crear_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario_view, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario_view, name='eliminar_usuario'),
]
