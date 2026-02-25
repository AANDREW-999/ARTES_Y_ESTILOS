<h1 align="center">Arte y Estilos Gestión Floral</h1>
<p align="center">Sistema web de gestión integral para la floristería Arte y Estilos</p>

<p align="center">
  <!-- Stack Django -->
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git" />
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
  <img src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail SMTP" />
</p>

---

## 📋 Descripción

Sistema web de gestión integral para la floristería **Arte y Estilos**, diseñado para digitalizar y optimizar los procesos del negocio de manera sencilla e intuitiva.

### ✨ Características Principales

- 🌸 **Gestión de clientes** - Registro y administración de clientes
- 📦 **Control de compras** - Gestión de compras y proveedores
- 🏪 **Administración de proveedores** - Catálogo de proveedores
- 👥 **Sistema de usuarios** - Autenticación y perfiles personalizados
- 📧 **Recuperación de contraseña** - Correos HTML con diseño floral elegante
- 🎨 **Interfaz moderna** - Diseño responsive con Bootstrap
- ♿ **Accesibilidad** - Funciones de accesibilidad integradas

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/ARTES_Y_ESTILOS.git
   cd ARTES_Y_ESTILOS
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   ```

3. **Activar entorno virtual:**
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar variables de entorno:**
   ```bash
   # Copiar el archivo de ejemplo
   copy .env.example .env
   ```
   
   Edita el archivo `.env` con tus credenciales de Gmail. Ver [Configuración de Email](#-configuración-de-email).

6. **Aplicar migraciones:**
   ```bash
   python manage.py migrate
   ```

7. **Crear superusuario:**
   ```bash
   python manage.py createsuperuser
   ```

8. **Ejecutar servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

9. **Acceder a la aplicación:**
   - Aplicación: http://localhost:8000
   - Panel de administración: http://localhost:8000/admin

---

## 📧 Configuración de Email

El sistema incluye recuperación de contraseña con correos HTML elegantes usando Gmail SMTP.

### Configuración Rápida

1. **Lee la guía completa:** `CONFIGURACION_EMAIL.md`

2. **Crea una cuenta Gmail** (o usa una existente)

3. **Genera una contraseña de aplicación:**
   - Ve a: https://myaccount.google.com/apppasswords
   - Activa la verificación en dos pasos
   - Genera una contraseña para "Correo"

4. **Configura el archivo `.env`:**
   ```env
   EMAIL_BACKEND=smtp
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu_correo@gmail.com
   EMAIL_HOST_PASSWORD=tu_contraseña_aplicacion
   DEFAULT_FROM_EMAIL=Arte y Estilos <tu_correo@gmail.com>
   ```

5. **Prueba la configuración:**
   ```bash
   python test_email_config.py
   ```

### Documentación Completa

- 📘 `LEEME_PRIMERO.md` - Índice y guía rápida
- 📗 `CONFIGURACION_EMAIL.md` - Guía de configuración paso a paso
- 📕 `RESUMEN_IMPLEMENTACION.md` - Resumen técnico completo
- 📙 `DISEÑO_CORREO.md` - Detalles del diseño HTML
- 📔 `BUENAS_PRACTICAS.md` - Seguridad y mejores prácticas

---

## 🛠️ Tecnologías

### Backend
- **Python 3.13** - Lenguaje de programación
- **Django 4.2** - Framework web
- **SQLite** - Base de datos

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos
- **JavaScript** - Interactividad
- **Bootstrap 5** - Framework CSS

### Utilidades
- **python-decouple** - Gestión de variables de entorno
- **Pillow** - Procesamiento de imágenes
- **django-bootstrap-v5** - Integración de Bootstrap

### Email
- **Gmail SMTP** - Servidor de correo
- **EmailMultiAlternatives** - Envío de correos HTML

---

## 📁 Estructura del Proyecto

```
ARTES_Y_ESTILOS/
├── ARTES_Y_ESTILOS/          # Configuración principal
│   ├── settings.py           # Configuración de Django
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # WSGI config
├── usuarios/                 # App de usuarios
│   ├── models.py             # Modelo Usuario y Perfil
│   ├── views.py              # Vistas (incluye recuperación)
│   ├── forms.py              # Formularios
│   └── templates/            # Templates
│       └── recuperar_password/
│           ├── email_recuperar_password.html
│           ├── email_recuperar_password.txt
│           └── ...
├── core/                     # App principal
├── clientes/                 # Gestión de clientes
├── proveedores/              # Gestión de proveedores
├── compras/                  # Gestión de compras
├── accesibilidad/            # Funciones de accesibilidad
├── static/                   # Archivos estáticos
├── media/                    # Archivos subidos
├── templates/                # Templates globales
├── .env                      # Variables de entorno (NO SUBIR A GIT)
├── .env.example              # Ejemplo de configuración
├── .gitignore                # Archivos ignorados por Git
├── manage.py                 # Comando de Django
├── requirements.txt          # Dependencias
├── test_email_config.py      # Script de prueba de email
└── *.md                      # Documentación
```

---

## 🔐 Seguridad

### Variables de Entorno

El archivo `.env` contiene información sensible y **NUNCA** debe subirse a Git:

```env
# ⚠️ NO SUBIR A GIT
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_aplicacion
SECRET_KEY=tu_clave_secreta
```

### Buenas Prácticas Implementadas

✅ Contraseñas de aplicación (no passwords reales)  
✅ Variables en `.env` (no en código)  
✅ `.env` en `.gitignore`  
✅ Sistema de tokens seguro de Django  
✅ Validación de contraseñas  
✅ CSRF protection habilitado  
✅ Sesiones seguras  

---

## 🧪 Testing

### Script de Prueba de Email

```bash
python test_email_config.py
```

Verifica:
- ✅ Configuración de email
- ✅ Templates de correo
- ✅ Archivo `.env`
- ✅ Envío de correo de prueba

### Tests de Django

```bash
python manage.py test
```

---

## 📚 Documentación

### Para Desarrolladores

- **`LEEME_PRIMERO.md`** - Índice y guía de inicio
- **`CONFIGURACION_EMAIL.md`** - Configurar Gmail SMTP
- **`RESUMEN_IMPLEMENTACION.md`** - Detalles técnicos
- **`DISEÑO_CORREO.md`** - Diseño del correo HTML
- **`BUENAS_PRACTICAS.md`** - Seguridad y mantenimiento

### Para Usuarios

- Panel de administración con interfaz intuitiva
- Formularios con validación en tiempo real
- Mensajes de éxito/error claros
- Diseño responsive para todos los dispositivos

---

## 👥 Autores

- **David Pedraza** - Desarrollo
- **Andres Pedraza** - Desarrollo
- **Mateo Becerra** - Desarrollo
- **Michael Ruiz** - Desarrollo
- **Nixon Zapata** - Desarrollo
- **Daniel Caceres** - Desarrollo

---

## 📄 Licencia

Este proyecto es privado y pertenece a **Arte y Estilos Gestión Floral**.

---

## 🆘 Soporte

### Problemas Comunes

#### Error de autenticación SMTP
- Verifica que la contraseña de aplicación sea correcta
- Asegúrate de tener 2FA activado en Gmail

#### No llegan los correos
- Revisa la carpeta de SPAM
- Verifica que el email esté registrado en el sistema

#### Error de módulos
```bash
pip install -r requirements.txt
```

### Más Ayuda

- Revisa la documentación en los archivos `.md`
- Ejecuta `python test_email_config.py` para diagnosticar
- Consulta `BUENAS_PRACTICAS.md` para solución de problemas

---

## 🎉 Características Destacadas

### Sistema de Correos HTML

- 🎨 Diseño floral elegante con identidad visual
- 📱 Responsive design para móviles
- ✉️ Compatible con todos los clientes de correo
- 🔐 Sistema de tokens seguro
- 💌 Personalización con nombre de usuario
- 🌸 Emojis florales y gradientes rosa

### Interfaz de Usuario

- 🎯 Diseño intuitivo y fácil de usar
- ⚡ Carga rápida y optimizada
- 📊 Dashboard con estadísticas
- 🔍 Búsqueda y filtros avanzados
- ♿ Funciones de accesibilidad

---

<p align="center">
  🌸 Hecho con ❤️ para Arte y Estilos Gestión Floral 🌸
</p>
