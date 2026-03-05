document.addEventListener('DOMContentLoaded', function () {

    /* ============================================================
       FORMATO Y VALIDACIÓN DE PRECIO
       ============================================================ */
    const precioDisplay = document.getElementById('precio-display');
    const precioReal    = document.getElementById('precio-real');
    const precioError   = document.getElementById('precio-error');

    function formatear(valor) {
        const soloDigitos = valor.replace(/\D/g, '');
        return soloDigitos.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    if (precioDisplay && precioReal) {
        // Formatear valor inicial (editar)
        if (precioDisplay.value) {
            const inicial = precioDisplay.value.replace(/\D/g, '');
            precioDisplay.value = formatear(inicial);
            precioReal.value    = inicial;
        }

        // Formatear mientras escribe
        precioDisplay.addEventListener('input', function () {
            const soloDigitos = this.value.replace(/\D/g, '');
            this.value        = formatear(soloDigitos);
            precioReal.value  = soloDigitos;

            // Limpiar error si ya escribió algo válido
            if (precioError && soloDigitos.length > 0) {
                precioError.style.display = 'none';
                precioDisplay.classList.remove('is-invalid');
            }
        });

        // Bloquear teclas no numéricas
        precioDisplay.addEventListener('keydown', function (e) {
            const permitidas = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Home', 'End'];
            if (!permitidas.includes(e.key) && !/^\d$/.test(e.key)) {
                e.preventDefault();
                if (precioError) {
                    precioError.textContent = 'Solo se permiten números.';
                    precioError.style.display = 'flex';
                    precioDisplay.classList.add('is-invalid');
                }
            }
        });

        // Bloquear pegar texto no numérico
        precioDisplay.addEventListener('paste', function (e) {
            e.preventDefault();
            const texto = (e.clipboardData || window.clipboardData).getData('text');
            const soloDigitos = texto.replace(/\D/g, '');
            if (soloDigitos) {
                this.value       = formatear(soloDigitos);
                precioReal.value = soloDigitos;
            }
        });
    }

    /* ============================================================
       VALIDACIÓN DE NOMBRE
       Solo letras (incluyendo acentos, ñ), espacios y guiones.
       No se permiten: números ni caracteres especiales (@, #, $, etc.)
       ============================================================ */
    const campoNombre = document.querySelector('input[name="nombre"]');
    const nombreError = document.getElementById('nombre-error');

    // Regex: letras unicode (cubre acentos y ñ), espacios y guiones
    const regexNombreValido   = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$/;
    const regexCaracterInvalido = /[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]/;

    if (campoNombre) {
        campoNombre.addEventListener('input', function () {
            const valor = this.value;

            if (valor === '') {
                if (nombreError) nombreError.style.display = 'none';
                this.classList.remove('is-invalid', 'is-valid');
                return;
            }

            if (regexCaracterInvalido.test(valor)) {
                // Mostrar error
                if (nombreError) {
                    nombreError.textContent = 'El nombre no puede contener números ni caracteres especiales.';
                    nombreError.style.display = 'flex';
                }
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else {
                // Válido
                if (nombreError) nombreError.style.display = 'none';
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });

        // Bloquear teclas inválidas en tiempo real
        campoNombre.addEventListener('keydown', function (e) {
            const permitidas = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight',
                                'Tab', 'Home', 'End', ' ', '-'];
            // Permitir letras (incluyendo acentos vía charCode > 127)
            if (e.key.length === 1 && !permitidas.includes(e.key)) {
                if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\-]$/.test(e.key) && e.key.charCodeAt(0) < 128) {
                    e.preventDefault();
                    if (nombreError) {
                        nombreError.textContent = 'El nombre no puede contener números ni caracteres especiales.';
                        nombreError.style.display = 'flex';
                    }
                    this.classList.add('is-invalid');
                }
            }
        });

        // Bloquear pegar texto inválido
        campoNombre.addEventListener('paste', function (e) {
            e.preventDefault();
            const texto = (e.clipboardData || window.clipboardData).getData('text');
            // Filtrar solo caracteres válidos
            const limpio = texto.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]/g, '');
            this.value += limpio;
            // Disparar input para validar
            this.dispatchEvent(new Event('input'));
        });
    }

    /* ============================================================
       VALIDAR AL ENVIAR EL FORMULARIO
       ============================================================ */
    const productForm = document.getElementById('product-form');

    // Función reutilizable para mostrar error en un campo
    function mostrarError(campo, errorEl, mensaje) {
        if (errorEl) {
            errorEl.textContent = mensaje;
            errorEl.style.display = 'flex';
        }
        if (campo) campo.classList.add('is-invalid');
    }

    // Función reutilizable para limpiar error
    function limpiarError(campo, errorEl) {
        if (errorEl) errorEl.style.display = 'none';
        if (campo) { campo.classList.remove('is-invalid'); campo.classList.add('is-valid'); }
    }

    if (productForm) {
        productForm.addEventListener('submit', function (e) {
            let valido = true;

            // ── Validar nombre ──────────────────────────────────
            if (campoNombre) {
                const valorNombre = campoNombre.value.trim();
                if (!valorNombre) {
                    mostrarError(campoNombre, nombreError, 'Este campo es obligatorio.');
                    valido = false;
                } else if (regexCaracterInvalido.test(valorNombre)) {
                    mostrarError(campoNombre, nombreError, 'El nombre no puede contener números ni caracteres especiales.');
                    valido = false;
                } else {
                    limpiarError(campoNombre, nombreError);
                }
            }

            // ── Validar precio ──────────────────────────────────
            if (precioReal) {
                if (!precioReal.value || precioReal.value.trim() === '') {
                    mostrarError(precioDisplay, precioError, 'Este campo es obligatorio.');
                    valido = false;
                } else if (precioReal.value === '0') {
                    mostrarError(precioDisplay, precioError, 'El precio debe ser mayor a 0.');
                    valido = false;
                } else {
                    limpiarError(precioDisplay, precioError);
                }
            }

            // ── Validar categoría ───────────────────────────────
            const campoCategoria  = document.querySelector('select[name="categoria"]');
            const categoriaError  = document.getElementById('categoria-error');
            if (campoCategoria && !campoCategoria.value) {
                mostrarError(campoCategoria, categoriaError, 'Este campo es obligatorio.');
                valido = false;
            } else if (campoCategoria) {
                limpiarError(campoCategoria, categoriaError);
            }

            // ── Validar tamaño ──────────────────────────────────
            const campoTamano  = document.querySelector('select[name="tamano"]');
            const tamanoError  = document.getElementById('tamano-error');
            if (campoTamano && !campoTamano.value) {
                mostrarError(campoTamano, tamanoError, 'Este campo es obligatorio.');
                valido = false;
            } else if (campoTamano) {
                limpiarError(campoTamano, tamanoError);
            }

            if (!valido) {
                e.preventDefault();
                // Scroll suave al primer error visible
                const primerError = productForm.querySelector('.is-invalid');
                if (primerError) primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }

});