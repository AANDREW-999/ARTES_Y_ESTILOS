/**
 * VALIDACIONES EN TIEMPO REAL PARA CLIENTES
 * Con bloqueo de caracteres inválidos y caracteres especiales
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // ========================================
    // CONFIGURACIÓN DE VALIDACIONES
    // ========================================
    const validaciones = {
        documento: {
            selector: '#id_documento',
            soloNumeros: true,
            permitirCaracteresEspeciales: false,
            validarLocal: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: false, mensaje: 'El documento es obligatorio' };
                }
                if (!/^\d+$/.test(valor)) {
                    return { valido: false, mensaje: 'Solo números permitidos' };
                }
                if (valor.length < 6) {
                    return { valido: false, mensaje: 'Debe tener al menos 6 dígitos' };
                }
                if (valor.length > 15) {
                    return { valido: false, mensaje: 'Debe tener máximo 15 dígitos' };
                }
                return { valido: true, mensaje: 'Verificando...' };
            }
        },
        nombre: {
            selector: '#id_nombre',
            soloLetras: true,
            permitirCaracteresEspeciales: false,
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: false, mensaje: 'El nombre es obligatorio' };
                }
                if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$/.test(valor)) {
                    return { valido: false, mensaje: 'Solo letras permitidas (sin números ni caracteres especiales)' };
                }
                if (valor.trim().length < 2) {
                    return { valido: false, mensaje: 'Debe tener al menos 2 caracteres' };
                }
                return { valido: true, mensaje: 'Nombre válido' };
            }
        },
        apellido: {
            selector: '#id_apellido',
            soloLetras: true,
            permitirCaracteresEspeciales: false,
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: false, mensaje: 'El apellido es obligatorio' };
                }
                if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$/.test(valor)) {
                    return { valido: false, mensaje: 'Solo letras permitidas (sin números ni caracteres especiales)' };
                }
                if (valor.trim().length < 2) {
                    return { valido: false, mensaje: 'Debe tener al menos 2 caracteres' };
                }
                return { valido: true, mensaje: 'Apellido válido' };
            }
        },
        telefono: {
            selector: '#id_telefono',
            soloNumeros: true,
            permitirEspacios: true,
            permitirCaracteresEspeciales: false,
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: true, mensaje: 'Opcional' };
                }
                const soloNumeros = valor.replace(/\s/g, '');
                if (!/^\d+$/.test(soloNumeros)) {
                    return { valido: false, mensaje: 'Solo números permitidos' };
                }
                if (soloNumeros.length < 7) {
                    return { valido: false, mensaje: 'Debe tener al menos 7 dígitos' };
                }
                if (soloNumeros.length > 15) {
                    return { valido: false, mensaje: 'Debe tener máximo 15 dígitos' };
                }
                return { valido: true, mensaje: 'Teléfono válido' };
            }
        },
        correo_electronico: {
            selector: '#id_correo_electronico',
            permitirCaracteresEspeciales: true,
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: true, mensaje: 'Opcional' };
                }
                const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!regex.test(valor)) {
                    return { valido: false, mensaje: 'Correo electrónico inválido (debe incluir @ y .)' };
                }
                return { valido: true, mensaje: 'Correo válido' };
            }
        },
        // ========================================
        // NUEVAS VALIDACIONES
        // ========================================
        departamento: {
            selector: '#id_departamento',
            validar: function(valor) {
                if (!valor || valor === '') {
                    return { valido: false, mensaje: 'Debe seleccionar un departamento' };
                }
                return { valido: true, mensaje: 'Departamento válido' };
            }
        },
        ciudad: {
            selector: '#id_ciudad',
            soloLetras: true,
            permitirCaracteresEspeciales: false,
            validar: function(valor) {
                const departamento = document.querySelector('#id_departamento')?.value;

                // Si hay departamento seleccionado, ciudad es obligatoria
                if (departamento && departamento !== '') {
                    if (!valor || valor.trim() === '') {
                        return { valido: false, mensaje: 'Debe seleccionar una ciudad' };
                    }
                    if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$/.test(valor)) {
                        return { valido: false, mensaje: 'Solo letras permitidas' };
                    }
                } else {
                    // Si no hay departamento, ciudad es opcional
                    if (!valor || valor.trim() === '') {
                        return { valido: true, mensaje: 'Opcional' };
                    }
                    if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$/.test(valor)) {
                        return { valido: false, mensaje: 'Solo letras permitidas' };
                    }
                }
                return { valido: true, mensaje: 'Ciudad válida' };
            }
        },
        direccion: {
            selector: '#id_direccion',
            permitirCaracteresEspeciales: false,
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: true, mensaje: 'Opcional' };
                }
                if (!/^[A-Za-z0-9ÁÉÍÓÚáéíóúñÑ\s\.,#\-]+$/.test(valor)) {
                    return { valido: false, mensaje: 'Caracteres especiales no permitidos (solo letras, números, ., ,, #, -)' };
                }
                return { valido: true, mensaje: 'Dirección válida' };
            }
        }
    };

    // ========================================
    // BLOQUEO DE TECLADO EN TIEMPO REAL
    // ========================================

    function bloquearCaracteresInvalidos(event) {
        const input = event.target;

        // Encontrar configuración del campo
        let config = null;
        for (let key in validaciones) {
            if (input.id === validaciones[key].selector.replace('#', '')) {
                config = validaciones[key];
                break;
            }
        }

        if (!config) return;

        // Teclas siempre permitidas (navegación, borrar, etc)
        const teclasPermitidas = [
            'Backspace', 'Delete', 'Tab', 'Escape', 'Enter',
            'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
            'Home', 'End', 'PageUp', 'PageDown',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'Control', 'Alt', 'Shift', 'Meta', 'CapsLock', 'NumLock', 'ScrollLock'
        ];

        // Permitir combinaciones con Ctrl (Ctrl+C, Ctrl+V, Ctrl+X, etc)
        if (event.ctrlKey || event.metaKey) return;

        // Permitir teclas de control
        if (teclasPermitidas.includes(event.key)) return;

        // BLOQUEO PARA CAMPOS DE SOLO NÚMEROS
        if (config.soloNumeros) {
            if (/^\d$/.test(event.key)) return;
            if (config.permitirEspacios && event.key === ' ') return;
            event.preventDefault();
            mostrarNotificacionTemporal(input, 'Solo números permitidos');
            return;
        }

        // BLOQUEO PARA CAMPOS DE SOLO LETRAS
        if (config.soloLetras) {
            if (/^[a-zA-ZáéíóúÁÉÍÓÚñÑ]$/.test(event.key)) return;
            if (event.key === ' ') return;
            event.preventDefault();
            mostrarNotificacionTemporal(input, 'Solo letras permitidas');
            return;
        }

        // BLOQUEO PARA CAMPOS SIN CARACTERES ESPECIALES
        if (!config.permitirCaracteresEspeciales && !config.soloLetras && !config.soloNumeros) {
            if (/^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]$/.test(event.key)) return;
            if (event.key === '.' || event.key === ',' || event.key === '-' || event.key === '#') return;
            event.preventDefault();
            mostrarNotificacionTemporal(input, 'Caracteres especiales no permitidos');
            return;
        }
    }

    // ========================================
    // NOTIFICACIÓN TEMPORAL
    // ========================================

    function mostrarNotificacionTemporal(input, mensaje) {
        const fieldWrapper = input.closest('.field-wrapper');
        if (!fieldWrapper) return;

        const notificacion = document.createElement('div');
        notificacion.className = 'field-error temporal';
        notificacion.style.opacity = '0.7';
        notificacion.style.fontSize = '0.75rem';
        notificacion.style.marginTop = '2px';
        notificacion.innerHTML = `<i class="bi bi-exclamation-circle-fill"></i> ${mensaje}`;

        const anteriores = fieldWrapper.querySelectorAll('.temporal');
        anteriores.forEach(el => el.remove());

        fieldWrapper.appendChild(notificacion);

        setTimeout(() => {
            if (notificacion.parentNode) {
                notificacion.remove();
            }
        }, 1500);
    }

    // ========================================
    // FUNCIONES DE FEEDBACK VISUAL
    // ========================================

    function limpiarFeedback(input) {
        const fieldWrapper = input.closest('.field-wrapper');
        if (!fieldWrapper) return;

        const mensajesAnteriores = fieldWrapper.querySelectorAll('.field-error:not(.temporal), .field-success, .field-warning');
        mensajesAnteriores.forEach(el => el.remove());

        input.classList.remove('is-valid', 'is-invalid', 'is-warning');
    }

    function mostrarFeedback(input, resultado) {
        const fieldWrapper = input.closest('.field-wrapper');
        if (!fieldWrapper) return;

        limpiarFeedback(input);

        const div = document.createElement('div');

        if (resultado.valido) {
            div.className = 'field-success';
            div.innerHTML = `<i class="bi bi-check-circle-fill"></i> ${resultado.mensaje}`;
            input.classList.add('is-valid');
        } else {
            div.className = 'field-error';
            div.innerHTML = `<i class="bi bi-exclamation-circle-fill"></i> ${resultado.mensaje}`;
            input.classList.add('is-invalid');
        }

        fieldWrapper.appendChild(div);
    }

    function mostrarCargando(input, mensaje = 'Verificando documento...') {
        const fieldWrapper = input.closest('.field-wrapper');
        if (!fieldWrapper) return;

        limpiarFeedback(input);

        const div = document.createElement('div');
        div.className = 'field-warning';
        div.innerHTML = `<i class="bi bi-hourglass-split"></i> ${mensaje}`;
        input.classList.add('is-warning');

        fieldWrapper.appendChild(div);
    }

    // ========================================
    // VALIDACIÓN DE DOCUMENTO EN SERVIDOR
    // ========================================

    let timeoutId;
    function validarDocumentoServidor(input, documentoId) {
        const currentId = document.querySelector('[name="cliente_id"]')?.value || '';

        fetch(`/clientes/verificar-documento/?documento=${encodeURIComponent(documentoId)}&exclude_id=${currentId}`)
            .then(response => response.json())
            .then(data => {
                if (data.existe) {
                    mostrarFeedback(input, {
                        valido: false,
                        mensaje: 'Este documento ya está registrado'
                    });
                } else {
                    mostrarFeedback(input, {
                        valido: true,
                        mensaje: 'Documento disponible'
                    });
                }
            })
            .catch(error => {
                console.error('Error verificando documento:', error);
                mostrarFeedback(input, {
                    valido: true,
                    mensaje: 'Documento válido (no se pudo verificar)'
                });
            });
    }

    // ========================================
    // INICIALIZAR VALIDACIONES
    // ========================================

    // AGREGAR EVENTO DE TECLADO A TODOS LOS CAMPOS
    for (let key in validaciones) {
        const config = validaciones[key];
        const input = document.querySelector(config.selector);

        if (input) {
            input.addEventListener('keydown', bloquearCaracteresInvalidos);

            if (key === 'documento') {
                input.addEventListener('input', function() {
                    const valor = this.value;
                    const resultadoLocal = validaciones.documento.validarLocal(valor);

                    if (!resultadoLocal.valido) {
                        mostrarFeedback(this, resultadoLocal);
                    } else {
                        mostrarCargando(this);

                        if (timeoutId) clearTimeout(timeoutId);

                        timeoutId = setTimeout(() => {
                            validarDocumentoServidor(this, valor);
                        }, 500);
                    }
                });
            } else {
                input.addEventListener('input', function() {
                    const resultado = config.validar(this.value);
                    mostrarFeedback(this, resultado);
                });
            }

            input.addEventListener('blur', function() {
                if (key === 'documento') {
                    if (this.value && this.classList.contains('is-warning')) {
                        const valor = this.value;
                        const resultadoLocal = validaciones.documento.validarLocal(valor);
                        if (resultadoLocal.valido) {
                            validarDocumentoServidor(this, valor);
                        }
                    }
                } else {
                    const resultado = config.validar(this.value);
                    mostrarFeedback(this, resultado);
                }
            });

            if (input.value) {
                setTimeout(() => {
                    if (key === 'documento') {
                        const resultadoLocal = validaciones.documento.validarLocal(input.value);
                        if (resultadoLocal.valido) {
                            mostrarCargando(input, 'Verificando documento existente...');
                            validarDocumentoServidor(input, input.value);
                        } else {
                            mostrarFeedback(input, resultadoLocal);
                        }
                    } else {
                        const resultado = config.validar(input.value);
                        mostrarFeedback(input, resultado);
                    }
                }, 100);
            }
        }
    }

    // ========================================
    // VALIDAR ANTES DE ENVIAR EL FORMULARIO
    // ========================================

    const formulario = document.querySelector('form');
    if (formulario) {
        formulario.addEventListener('submit', function(e) {
            let formularioValido = true;

            for (let key in validaciones) {
                const config = validaciones[key];
                const input = document.querySelector(config.selector);

                if (input) {
                    if (key === 'documento') {
                        const resultadoLocal = validaciones.documento.validarLocal(input.value);
                        if (!resultadoLocal.valido) {
                            formularioValido = false;
                            mostrarFeedback(input, resultadoLocal);
                        } else if (input.classList.contains('is-warning')) {
                            e.preventDefault();
                            mostrarCargando(input, 'Esperando verificación del documento...');
                            setTimeout(() => {
                                alert('Por favor espere a que se verifique el documento.');
                            }, 100);
                            return;
                        }
                    } else {
                        const resultado = config.validar(input.value);
                        mostrarFeedback(input, resultado);
                        if (!resultado.valido) {
                            formularioValido = false;
                        }
                    }
                }
            }

            if (!formularioValido) {
                e.preventDefault();

                const alertaAnterior = document.querySelector('.alert-danger-box');
                if (alertaAnterior) alertaAnterior.remove();

                const alerta = document.createElement('div');
                alerta.className = 'alert-danger-box mb-4';
                alerta.innerHTML = `
                    <i class="bi bi-exclamation-triangle-fill"></i>
                    <div>Por favor, corrija los errores en el formulario antes de guardar.</div>
                `;

                formulario.insertBefore(alerta, formulario.firstChild);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }
});