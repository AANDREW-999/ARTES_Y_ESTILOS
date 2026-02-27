/**
 * VALIDACIONES EN TIEMPO REAL PARA CLIENTES
 * Con validación de documento existente vía AJAX
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // ========================================
    // CONFIGURACIÓN DE VALIDACIONES
    // ========================================
    const validaciones = {
        documento: {
            selector: '#id_documento',
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
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: false, mensaje: 'El nombre es obligatorio' };
                }
                if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$/.test(valor)) {
                    return { valido: false, mensaje: 'Solo letras permitidas' };
                }
                if (valor.trim().length < 2) {
                    return { valido: false, mensaje: 'Debe tener al menos 2 caracteres' };
                }
                return { valido: true, mensaje: 'Nombre válido' };
            }
        },
        apellido: {
            selector: '#id_apellido',
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: false, mensaje: 'El apellido es obligatorio' };
                }
                if (!/^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$/.test(valor)) {
                    return { valido: false, mensaje: 'Solo letras permitidas' };
                }
                if (valor.trim().length < 2) {
                    return { valido: false, mensaje: 'Debe tener al menos 2 caracteres' };
                }
                return { valido: true, mensaje: 'Apellido válido' };
            }
        },
        telefono: {
            selector: '#id_telefono',
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
            validar: function(valor) {
                if (!valor || valor.trim() === '') {
                    return { valido: true, mensaje: 'Opcional' };
                }
                const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!regex.test(valor)) {
                    return { valido: false, mensaje: 'Correo electrónico inválido' };
                }
                return { valido: true, mensaje: 'Correo válido' };
            }
        }
    };

    // ========================================
    // FUNCIONES DE FEEDBACK VISUAL
    // ========================================

    function limpiarFeedback(input) {
        const fieldWrapper = input.closest('.field-wrapper');
        if (!fieldWrapper) return;

        const mensajesAnteriores = fieldWrapper.querySelectorAll('.field-error, .field-success, .field-warning');
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
        // Obtener el ID del cliente actual (si es edición)
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

    // Campo documento con validación especial
    const docInput = document.querySelector('#id_documento');
    if (docInput) {
        // Agregar hidden con el ID si es edición
        const isEditing = document.querySelector('[name="cliente_id"]') ||
                         document.querySelector('.profile-name')?.textContent.includes('Editar');

        if (!document.querySelector('[name="cliente_id"]')) {
            const hiddenId = document.createElement('input');
            hiddenId.type = 'hidden';
            hiddenId.name = 'cliente_id';
            // Intentar obtener el ID de la URL
            const matches = window.location.pathname.match(/\/(\d+)\/editar/);
            if (matches) {
                hiddenId.value = matches[1];
            }
            document.querySelector('form')?.appendChild(hiddenId);
        }

        docInput.addEventListener('input', function() {
            const valor = this.value;
            const resultadoLocal = validaciones.documento.validarLocal(valor);

            if (!resultadoLocal.valido) {
                // Error local (formato, longitud, etc)
                mostrarFeedback(this, resultadoLocal);
            } else {
                // Formato válido, ahora verificar en servidor
                mostrarCargando(this);

                // Limpiar timeout anterior
                if (timeoutId) clearTimeout(timeoutId);

                // Esperar 500ms después de dejar de escribir
                timeoutId = setTimeout(() => {
                    validarDocumentoServidor(this, valor);
                }, 500);
            }
        });

        docInput.addEventListener('blur', function() {
            if (this.value && this.classList.contains('is-warning')) {
                // Si quedó en estado warning, forzar verificación
                const valor = this.value;
                const resultadoLocal = validaciones.documento.validarLocal(valor);
                if (resultadoLocal.valido) {
                    validarDocumentoServidor(this, valor);
                }
            }
        });

        // Validar al cargar si tiene valor
        if (docInput.value) {
            setTimeout(() => {
                const resultadoLocal = validaciones.documento.validarLocal(docInput.value);
                if (resultadoLocal.valido) {
                    mostrarCargando(docInput, 'Verificando documento existente...');
                    validarDocumentoServidor(docInput, docInput.value);
                } else {
                    mostrarFeedback(docInput, resultadoLocal);
                }
            }, 100);
        }
    }

    // Resto de campos
    for (let key in validaciones) {
        if (key === 'documento') continue;

        const config = validaciones[key];
        const input = document.querySelector(config.selector);

        if (input) {
            input.addEventListener('input', function() {
                const resultado = config.validar(this.value);
                mostrarFeedback(this, resultado);
            });

            input.addEventListener('blur', function() {
                const resultado = config.validar(this.value);
                mostrarFeedback(this, resultado);
            });

            if (input.value) {
                setTimeout(() => {
                    const resultado = config.validar(input.value);
                    mostrarFeedback(input, resultado);
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

            // Validar documento de forma especial
            if (docInput && docInput.value) {
                const resultadoLocal = validaciones.documento.validarLocal(docInput.value);
                if (!resultadoLocal.valido) {
                    formularioValido = false;
                    mostrarFeedback(docInput, resultadoLocal);
                } else if (docInput.classList.contains('is-warning')) {
                    // Si aún está verificando, esperar
                    e.preventDefault();
                    mostrarCargando(docInput, 'Esperando verificación del documento...');
                    setTimeout(() => {
                        alert('Por favor espere a que se verifique el documento.');
                    }, 100);
                    return;
                }
            }

            // Validar otros campos
            for (let key in validaciones) {
                if (key === 'documento') continue;

                const config = validaciones[key];
                const input = document.querySelector(config.selector);

                if (input) {
                    const resultado = config.validar(input.value);
                    mostrarFeedback(input, resultado);
                    if (!resultado.valido) {
                        formularioValido = false;
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