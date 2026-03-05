/**
 * VALIDACIONES EN TIEMPO REAL
 * Con bloqueo de caracteres inválidos y caracteres especiales
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // ========================================
    // CONFIGURACIÓN DE VALIDACIONES
    // ========================================
    const validaciones = {
        documento: {
            selector: ['#id_documento'],
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
                if (valor.length > 10) {
                    return { valido: false, mensaje: 'Debe tener máximo 10 dígitos' };
                }
                return { valido: true, mensaje: 'Verificando...' };
            }
        },
        nombre: {
            selector: ['#id_nombre', '#id_first_name'],
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
            selector: ['#id_apellido', '#id_last_name'],
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
            selector: ['#id_telefono'],
            soloNumeros: true,
            permitirEspacios: true,
            permitirCaracteresEspeciales: false,
            validar: function(valor, input) {
                if (!valor || valor.trim() === '') {
                    if (input && input.required) {
                        return { valido: false, mensaje: 'El teléfono es obligatorio' };
                    }
                    return { valido: true, mensaje: 'Opcional' };
                }
                if (input && input.maxLength > 0 && valor.length > input.maxLength) {
                    return { valido: false, mensaje: `Debe tener máximo ${input.maxLength} caracteres` };
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
            selector: ['#id_correo_electronico', '#id_email'],
            permitirCaracteresEspeciales: true,
            validar: function(valor, input) {
                if (!valor || valor.trim() === '') {
                    if (input && input.required) {
                        return { valido: false, mensaje: 'El correo electrónico es obligatorio' };
                    }
                    return { valido: true, mensaje: 'Opcional' };
                }
                if (input && input.maxLength > 0 && valor.length > input.maxLength) {
                    return { valido: false, mensaje: `Debe tener máximo ${input.maxLength} caracteres` };
                }
                const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!regex.test(valor)) {
                    return { valido: false, mensaje: 'Correo electrónico inválido (debe incluir @ y .)' };
                }
                return { valido: true, mensaje: 'Correo válido' };
            }
        },
        nombre_usuario: {
            selector: ['#id_username'],
            permitirCaracteresEspeciales: true,
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: false, mensaje: 'El nombre de usuario es obligatorio' };
                }
                const trimmed = valor.trim();
                if (trimmed.length < 4) {
                    return { valido: false, mensaje: 'Debe tener al menos 4 caracteres' };
                }
                if (!/^[a-zA-Z0-9_-]+$/.test(trimmed)) {
                    return { valido: false, mensaje: 'Solo letras, números, guiones (-) y guiones bajos (_)' };
                }
                return { valido: true, mensaje: 'Nombre de usuario válido' };
            }
        },
        fecha_nacimiento: {
            selector: ['#id_fecha_nacimiento'],
            permitirCaracteresEspeciales: true,
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: true, mensaje: 'Opcional' };
                }
                const fecha = new Date(valor);
                if (Number.isNaN(fecha.getTime())) {
                    return { valido: false, mensaje: 'Fecha inválida' };
                }
                const hoy = new Date();
                hoy.setHours(0, 0, 0, 0);
                if (fecha > hoy) {
                    return { valido: false, mensaje: 'La fecha no puede ser futura' };
                }
                const limite = new Date('1900-01-01');
                if (fecha < limite) {
                    return { valido: false, mensaje: 'La fecha es demasiado antigua' };
                }
                return { valido: true, mensaje: 'Fecha válida' };
            }
        },
        // ========================================
        // NUEVAS VALIDACIONES
        // ========================================
        departamento: {
            selector: ['#id_departamento'],
            validar: function(valor) {
                if (!valor || valor === '') {
                    return { valido: false, mensaje: 'Debe seleccionar un departamento' };
                }
                return { valido: true, mensaje: 'Departamento válido' };
            }
        },
        ciudad: {
            selector: ['#id_ciudad'],
            soloLetras: true,
            permitirCaracteresEspeciales: false,
            validar: function(valor, input) {
                const departamento = document.querySelector('#id_departamento')?.value;

                // Si hay departamento seleccionado, ciudad es obligatoria
                if (departamento && departamento !== '') {
                    if (!valor || valor.trim() === '') {
                        return { valido: false, mensaje: 'Debe seleccionar una ciudad' };
                    }
                    if (input && input.maxLength > 0 && valor.length > input.maxLength) {
                        return { valido: false, mensaje: `Debe tener máximo ${input.maxLength} caracteres` };
                    }
                    if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$/.test(valor)) {
                        return { valido: false, mensaje: 'Solo letras permitidas' };
                    }
                } else {
                    // Si no hay departamento, ciudad es opcional
                    if (!valor || valor.trim() === '') {
                        if (input && input.required) {
                            return { valido: false, mensaje: 'La ciudad es obligatoria' };
                        }
                        return { valido: true, mensaje: 'Opcional' };
                    }
                    if (input && input.maxLength > 0 && valor.length > input.maxLength) {
                        return { valido: false, mensaje: `Debe tener máximo ${input.maxLength} caracteres` };
                    }
                    if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$/.test(valor)) {
                        return { valido: false, mensaje: 'Solo letras permitidas' };
                    }
                }
                return { valido: true, mensaje: 'Ciudad válida' };
            }
        },
        direccion: {
            selector: ['#id_direccion'],
            permitirCaracteresEspeciales: false,
            validar: function(valor, input) {
                if (!valor || valor.trim() === '') {
                    if (input && input.required) {
                        return { valido: false, mensaje: 'La dirección es obligatoria' };
                    }
                    return { valido: true, mensaje: 'Opcional' };
                }
                if (input && input.maxLength > 0 && valor.length > input.maxLength) {
                    return { valido: false, mensaje: `Debe tener máximo ${input.maxLength} caracteres` };
                }
                if (!/^[A-Za-z0-9ÁÉÍÓÚáéíóúñÑ\s\.,#\-]+$/.test(valor)) {
                    return { valido: false, mensaje: 'Caracteres especiales no permitidos (solo letras, números, ., ,, #, -)' };
                }
                return { valido: true, mensaje: 'Dirección válida' };
            }
        },

        // ========================================
        // PROVEEDORES
        // ========================================
        tipo_documento_proveedor: {
            selector: ['#id_tipo_documento'],
            permitirCaracteresEspeciales: true,
            validar: function(valor) {
                if (!valor || valor === '') {
                    return { valido: false, mensaje: 'Debe seleccionar el tipo de documento' };
                }
                return { valido: true, mensaje: 'Tipo de documento válido' };
            }
        },
        numero_documento_proveedor: {
            selector: ['#id_numero_documento'],
            soloNumeros: true,
            permitirCaracteresEspeciales: false,
            validarLocal: function(valor, input) {
                if (!valor || valor.trim() === '') {
                    return { valido: false, mensaje: 'El número de documento es obligatorio' };
                }

                const trimmed = valor.trim();
                if (!/^\d+$/.test(trimmed)) {
                    return { valido: false, mensaje: 'Solo números permitidos' };
                }

                const maxLen = (input && input.maxLength > 0) ? input.maxLength : 10;
                if (trimmed.length < 6) {
                    return { valido: false, mensaje: 'Debe tener al menos 6 dígitos' };
                }
                if (trimmed.length > maxLen) {
                    return { valido: false, mensaje: `Debe tener máximo ${maxLen} dígitos` };
                }

                return { valido: true, mensaje: 'Verificando...' };
            },
            validar: function(valor) {
                const input = document.querySelector('#id_numero_documento');
                const local = this.validarLocal(valor, input);
                if (!local.valido) return local;
                return { valido: true, mensaje: 'Documento válido' };
            }
        },
        nombre_proveedor: {
            selector: ['#id_nombre_proveedor'],
            soloLetras: true,
            permitirCaracteresEspeciales: false,
            validar: function(valor, input) {
                if (!valor || valor.trim() === '') {
                    return { valido: false, mensaje: 'El nombre del proveedor es obligatorio' };
                }
                const trimmed = valor.trim();
                if (trimmed.length < 2) {
                    return { valido: false, mensaje: 'Debe tener al menos 2 caracteres' };
                }
                if (input && input.maxLength > 0 && trimmed.length > input.maxLength) {
                    return { valido: false, mensaje: `Debe tener máximo ${input.maxLength} caracteres` };
                }
                if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$/.test(trimmed)) {
                    return { valido: false, mensaje: 'Solo letras permitidas (sin números ni caracteres especiales)' };
                }
                return { valido: true, mensaje: 'Nombre válido' };
            }
        }
    };

    // ========================================
    // BLOQUEO DE TECLADO EN TIEMPO REAL
    // ========================================

    function getSelectors(config) {
        if (Array.isArray(config.selector)) {
            return config.selector;
        }
        return [config.selector];
    }

    function getFieldWrapper(input) {
        return input.closest('.field-wrapper') || input.closest('.form-floating') || input.closest('.mb-3') || input.parentElement;
    }

    function bloquearCaracteresInvalidos(event) {
        const input = event.target;

        // Encontrar configuración del campo
        let config = null;
        for (let key in validaciones) {
            const selectors = getSelectors(validaciones[key]);
            for (let i = 0; i < selectors.length; i++) {
                if (input.id === selectors[i].replace('#', '')) {
                    config = validaciones[key];
                    break;
                }
            }
            if (config) break;
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

    function normalizarValorSegunConfig(input, config) {
        if (!input || !config) return;

        if (config.soloNumeros) {
            const valorAnterior = input.value;
            const soloDigitos = config.permitirEspacios
                ? valorAnterior.replace(/[^\d\s]/g, '')
                : valorAnterior.replace(/\D/g, '');

            if (soloDigitos !== valorAnterior) {
                const start = input.selectionStart;
                const end = input.selectionEnd;
                input.value = soloDigitos;
                try {
                    const delta = valorAnterior.length - soloDigitos.length;
                    const newPos = Math.max(0, (start || 0) - delta);
                    input.setSelectionRange(newPos, newPos);
                } catch (_) {
                    // Algunos navegadores/inputs no soportan setSelectionRange
                }
                mostrarNotificacionTemporal(input, 'Solo números permitidos');
            }
        }

        if (config.soloLetras) {
            const valorAnterior = input.value;
            const soloLetrasYEspacios = valorAnterior.replace(/[^A-Za-zÁÉÍÓÚáéíóúñÑ\s]/g, '');
            if (soloLetrasYEspacios !== valorAnterior) {
                const start = input.selectionStart;
                input.value = soloLetrasYEspacios;
                try {
                    const delta = valorAnterior.length - soloLetrasYEspacios.length;
                    const newPos = Math.max(0, (start || 0) - delta);
                    input.setSelectionRange(newPos, newPos);
                } catch (_) {
                    // noop
                }
                mostrarNotificacionTemporal(input, 'Solo letras permitidas');
            }
        }
    }

    // ========================================
    // NOTIFICACIÓN TEMPORAL
    // ========================================

    function mostrarNotificacionTemporal(input, mensaje) {
        const fieldWrapper = getFieldWrapper(input);
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
        const fieldWrapper = getFieldWrapper(input);
        if (!fieldWrapper) return;

        const mensajesAnteriores = fieldWrapper.querySelectorAll('.field-error:not(.temporal), .field-success, .field-warning');
        mensajesAnteriores.forEach(el => el.remove());

        const invalidFeedback = fieldWrapper.querySelector('.invalid-feedback');
        const validFeedback = fieldWrapper.querySelector('.valid-feedback');
        if (invalidFeedback) {
            invalidFeedback.textContent = '';
            invalidFeedback.style.display = 'none';
        }
        if (validFeedback) {
            validFeedback.textContent = '';
            validFeedback.style.display = 'none';
        }

        input.classList.remove('is-valid', 'is-invalid', 'is-warning');
    }

    function mostrarFeedback(input, resultado) {
        const fieldWrapper = getFieldWrapper(input);
        if (!fieldWrapper) return;

        limpiarFeedback(input);

        const invalidFeedback = fieldWrapper.querySelector('.invalid-feedback');
        const validFeedback = fieldWrapper.querySelector('.valid-feedback');

        if (resultado.valido) {
            input.classList.add('is-valid');
            if (validFeedback) {
                validFeedback.innerHTML = `<i class="bi bi-check-circle-fill"></i> ${resultado.mensaje}`;
                validFeedback.style.display = 'block';
            } else {
                const div = document.createElement('div');
                div.className = 'field-success';
                div.innerHTML = `<i class="bi bi-check-circle-fill"></i> ${resultado.mensaje}`;
                fieldWrapper.appendChild(div);
            }
        } else {
            input.classList.add('is-invalid');
            if (invalidFeedback) {
                invalidFeedback.innerHTML = `<i class="bi bi-exclamation-circle-fill"></i> ${resultado.mensaje}`;
                invalidFeedback.style.display = 'block';
            } else {
                const div = document.createElement('div');
                div.className = 'field-error';
                div.innerHTML = `<i class="bi bi-exclamation-circle-fill"></i> ${resultado.mensaje}`;
                fieldWrapper.appendChild(div);
            }
        }
    }

    function mostrarCargando(input, mensaje = 'Verificando documento...') {
        const fieldWrapper = getFieldWrapper(input);
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
    function validarDocumentoServidor(input, documentoId, verifyUrl) {
        const currentId =
            document.querySelector('[name="exclude_id"]')?.value ||
            document.querySelector('[name="cliente_id"]')?.value ||
            document.querySelector('[name="proveedor_id"]')?.value ||
            '';
        const url = verifyUrl || '/clientes/verificar-documento/';

        fetch(`${url}?documento=${encodeURIComponent(documentoId)}&exclude_id=${currentId}`)
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
        const selectors = getSelectors(config);

        selectors.forEach(selector => {
            const input = document.querySelector(selector);

            if (input) {
                input.addEventListener('keydown', bloquearCaracteresInvalidos);

                const tieneValidacionDocumento = typeof config.validarLocal === 'function';

                if (tieneValidacionDocumento) {
                    const handlerDocumento = function() {
                        normalizarValorSegunConfig(this, config);
                        const valor = this.value;
                        const resultadoLocal = config.validarLocal(valor, this);
                        const verifyUrl = this.dataset.verificarUrl;

                        if (!resultadoLocal.valido) {
                            mostrarFeedback(this, resultadoLocal);
                        } else if (!verifyUrl) {
                            mostrarFeedback(this, { valido: true, mensaje: 'Documento válido' });
                        } else {
                            mostrarCargando(this);

                            if (timeoutId) clearTimeout(timeoutId);

                            timeoutId = setTimeout(() => {
                                validarDocumentoServidor(this, valor, verifyUrl);
                            }, 500);
                        }
                    };

                    input.addEventListener('input', handlerDocumento);
                    if (input.tagName === 'SELECT') {
                        input.addEventListener('change', handlerDocumento);
                    }
                } else {
                    const handlerNormal = function() {
                        normalizarValorSegunConfig(this, config);
                        const resultado = config.validar(this.value, this);
                        mostrarFeedback(this, resultado);
                    };

                    input.addEventListener('input', handlerNormal);
                    if (input.tagName === 'SELECT') {
                        input.addEventListener('change', handlerNormal);
                    }
                }

                input.addEventListener('blur', function() {
                    if (tieneValidacionDocumento) {
                        if (this.value && this.classList.contains('is-warning')) {
                            const valor = this.value;
                            const resultadoLocal = config.validarLocal(valor, this);
                            const verifyUrl = this.dataset.verificarUrl;
                            if (resultadoLocal.valido && verifyUrl) {
                                validarDocumentoServidor(this, valor, verifyUrl);
                            }
                        }
                    } else {
                        const resultado = config.validar(this.value, this);
                        mostrarFeedback(this, resultado);
                    }
                });

                if (input.value) {
                    setTimeout(() => {
                        if (tieneValidacionDocumento) {
                            const resultadoLocal = config.validarLocal(input.value, input);
                            const verifyUrl = input.dataset.verificarUrl;
                            if (resultadoLocal.valido && verifyUrl) {
                                mostrarCargando(input, 'Verificando documento existente...');
                                validarDocumentoServidor(input, input.value, verifyUrl);
                            } else if (resultadoLocal.valido) {
                                mostrarFeedback(input, { valido: true, mensaje: 'Documento válido' });
                            } else {
                                mostrarFeedback(input, resultadoLocal);
                            }
                        } else {
                            const resultado = config.validar(input.value, input);
                            mostrarFeedback(input, resultado);
                        }
                    }, 100);
                }
            }
        });
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
                const selectors = getSelectors(config);

                selectors.forEach(selector => {
                    const input = document.querySelector(selector);

                    if (input) {
                        const tieneValidacionDocumento = typeof config.validarLocal === 'function';

                        if (tieneValidacionDocumento) {
                            const resultadoLocal = config.validarLocal(input.value, input);
                            const verifyUrl = input.dataset.verificarUrl;
                            if (!resultadoLocal.valido) {
                                formularioValido = false;
                                mostrarFeedback(input, resultadoLocal);
                            } else if (input.classList.contains('is-warning') && verifyUrl) {
                                e.preventDefault();
                                mostrarCargando(input, 'Esperando verificación del documento...');
                                setTimeout(() => {
                                    alert('Por favor espere a que se verifique el documento.');
                                }, 100);
                                return;
                            }
                        } else {
                            const resultado = config.validar(input.value, input);
                            mostrarFeedback(input, resultado);
                            if (!resultado.valido) {
                                formularioValido = false;
                            }
                        }
                    }
                });
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