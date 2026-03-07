<h1 align="center">Arte & Estilos · Gestión Floral</h1>
<p align="center">Plataforma web para la administración y vitrina digital de la Floristería <strong>Arte & Estilos</strong>.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
  <img src="https://img.shields.io/badge/Gmail%20SMTP-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail SMTP" />
</p>

---

## 🌸 Descripción

**Arte & Estilos · Gestión Floral** es un sistema web desarrollado con **Django** para digitalizar la operación de una floristería: catálogo, gestión de usuarios, clientes, compras, proveedores y ventas; con una interfaz moderna y una identidad visual **floral**.

El proyecto combina:

- **Landing / Vitrina** para mostrar el catálogo y la marca.
- **Autenticación completa** (login, registro y recuperación de contraseña por email).
- **Panel Administrativo** con gestión de módulos (CRUD) y **selector de tema oscuro/claro**.

---

## ✨ Características destacadas

### 🖥️ Experiencia de Usuario (UI/UX)

- **Identidad floral**: paleta cálida, tipografías elegantes y componentes inspirados en una estética boutique.
- **Index (Landing)**: vitrina floral con componentes de catálogo, secciones informativas y contacto.
- **Login/Registro/Recuperación**: pantallas de autenticación con estética “nocturna” (fondos tipo slideshow) y efecto glassmorphism para una lectura cómoda.
- **Modo oscuro/claro en el Panel Administrativo**: alternancia con persistencia (guardado en el navegador) para trabajar cómodo de día o de noche.
- **Interfaz responsive**: optimizada para escritorio y móvil con Bootstrap.
- **Notificaciones (toasts)** y feedback visual en formularios.

### 🔐 Autenticación y cuentas

- **Usuario personalizado** con documento y correo único.
- **Registro** de usuarios.
- **Gestión de usuarios** desde el panel (crear, editar, activar/desactivar, convertir a superadmin, eliminación controlada).
- **Perfiles** con foto, datos de contacto y campos adicionales.

### 📧 Recuperación de contraseña (Email)

- Flujo completo de **solicitud → confirmación → actualización**.
- Envío de correo con **plantillas HTML y texto plano** (estilo floral).
- Backend de correo configurable: por defecto **consola** (desarrollo) y opcional **SMTP** (producción).

### 🧾 Operación del negocio

- **Clientes**: registro, edición, detalle y eliminación.
- **Proveedores**: administración de proveedores (activos/inactivos).
- **Compras**: compras con detalles por ítem (flor o producto), subtotal y total.
- **Ventas**: ventas con detalles, recálculo de totales, IVA configurable, domicilios y mano de obra.
- **Catálogo**: productos del catálogo asociados a categorías e imagen.

### ♿ Accesibilidad

- Módulo de accesibilidad integrado mediante template tags (widget embebible).

---

## 🧩 Módulos y modelos (resumen)

Este repositorio está organizado por apps de Django. Principales entidades:

- **Usuarios**
  - `Usuario` (custom user basado en `AbstractUser`) + `Perfil` (1:1)
- **Clientes**
  - `Cliente`
- **Proveedores**
  - `Proveedor`
- **Compras**
  - `Compra` + `DetalleCompra` (líneas por flor o producto)
- **Ventas**
  - `Venta` + `DetalleVenta` (líneas por flor o producto, IVA y totales)
- **Categorías**
  - `Categoria`
- **Catálogo**
  - `Producto` (producto del catálogo con categoría e imagen)
- **Inventario complementario**
  - `Flor` (stock y tipo de flor)
  - `Producto` (app `producto`: chocolates, globos, tarjetas, etc.)

---

## 🚀 Instalación (local)

### Requisitos

- **Python 3.10+**
- **pip**
- **Git**

### Pasos

1. Clona el repositorio:
   ```bash
   git clone https://github.com/AANDREW-999/ARTES_Y_ESTILOS.git
   cd ARTES_Y_ESTILOS
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   ```

   Windows (PowerShell):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Aplica migraciones:
   ```bash
   python manage.py migrate
   ```

5. Crea un superusuario:
   ```bash
   python manage.py createsuperuser
   ```

6. Ejecuta el servidor:
   ```bash
   python manage.py runserver
   ```

7. Abre en el navegador:
   - App: http://localhost:8000

---

## 📧 Configuración de Email (opcional)

El proyecto permite cambiar entre backend de consola (por defecto) y SMTP mediante variables de entorno leídas desde `.env` (con `python-decouple`).

### Opción A — Desarrollo (recomendado)

- No necesitas configurar nada: por defecto el correo se escribe en consola.

### Opción B — SMTP (Gmail)

1. Crea (o edita) el archivo `.env` en la raíz del proyecto.
2. Agrega:

   ```env
   EMAIL_BACKEND=smtp
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu_correo@gmail.com
   EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicación
   DEFAULT_FROM_EMAIL=Arte & Estilos <tu_correo@gmail.com>
   ```

> Recomendación: usa una **contraseña de aplicación** y ten **2FA** habilitado.

---

## 🧪 Tests

Ejecuta el set de pruebas de Django:

```bash
python manage.py test
```

---

## 🗂️ Estructura del proyecto (alto nivel)

```
ARTES_Y_ESTILOS/
├── ARTES_Y_ESTILOS/         # Configuración del proyecto (settings/urls/asgi/wsgi)
├── core/                    # Landing (index), contacto, emails de contacto, páginas base
├── usuarios/                # Auth, perfiles, gestión de usuarios y recuperación por email
├── clientes/                # CRUD de clientes
├── proveedores/             # CRUD de proveedores
├── compras/                 # Compras + detalles (flor/producto)
├── ventas/                  # Ventas + detalles (flor/producto)
├── categoria/               # Categorías
├── catalogo/                # Catálogo público/gestión de productos del catálogo
├── flor/                    # Inventario de flores
├── producto/                # Inventario de complementos (chocolates, globos, etc.)
├── accesibilidad/           # Widget/funciones de accesibilidad
├── templates/               # Base templates (master / panel admin)
├── static/                  # Estáticos globales
├── media/                   # Subidas (fotos de perfiles, flores, productos, etc.)
└── db.sqlite3               # BD local por defecto
```

---

## 🔐 Seguridad (mínimos recomendados)

- Mantén `.env` fuera de Git (ya está en `.gitignore`).
- Evita reutilizar contraseñas personales en SMTP: utiliza **contraseñas de aplicación**.
- Django incluye protección CSRF, sesiones y validación de formularios.

---

## 👥 Equipo

**Arte & Estilos · Gestión Floral** fue construido por un equipo con enfoque full‑stack, cuidando tanto la operación como la experiencia visual.

- **Andrés González** — Full Stack Developer
- **Nixon Zapata** — Full Stack Developer
- **David Pedraza** — Full Stack Developer
- **Mateo Becerra** — Full Stack Developer
- **Alison** — Frontend Developer
- **Daniel Cáceres** — Backend Developer

---

## 📄 Licencia

Proyecto privado. Propiedad de **Arte & Estilos · Gestión Floral**.

---

<p align="center">🌸 Hecho con cariño, código y flores para Arte & Estilos 🌸</p>
