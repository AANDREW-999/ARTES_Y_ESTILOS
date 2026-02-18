/**
 * REGISTRO.JS - Sistema de validación UX profesional con Bootstrap 5
 * Versión optimizada con animaciones y feedback dinámico
 * @version 3.0
 * @date 2026-02-13
 */

(function() {
  'use strict';

  // ============================================================================
  // CLASE PRINCIPAL DE VALIDACIÓN
  // ============================================================================
  class RegistroValidator {
    constructor() {
      this.toasts = {
        success: null,
        error: null,
        warning: null
      };

      this.fieldsToValidate = [
        'id_documento',
        'id_email',
        'id_username',
        'id_first_name',
        'id_last_name',
        'id_password1',
        'id_password2'
      ];

      this.passwordRequirements = {
        length: { regex: /.{8,}/, element: 'req-length', text: 'Mínimo 8 caracteres' },
        lowercase: { regex: /[a-z]/, element: 'req-lowercase', text: 'Al menos una minúscula' },
        uppercase: { regex: /[A-Z]/, element: 'req-uppercase', text: 'Al menos una mayúscula' },
        number: { regex: /[0-9]/, element: 'req-number', text: 'Al menos un número' },
        special: { regex: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/? ]/, element: 'req-special', text: 'Al menos un carácter especial' }
      };
    }


    // ========================================================================
    // INICIALIZACIÓN PRINCIPAL
    // ========================================================================
    initialize() {
      console.log('🚀 Iniciando sistema de validación...');

      // Verificar que Bootstrap esté disponible
      if (typeof bootstrap === 'undefined') {
        console.error('❌ Bootstrap no está cargado');
        return;
      }

      this.cleanFormOnLoad(); // Limpiar formulario al inicio
      this.initializeToasts();
      this.convertDjangoMessages();
      this.initializePasswordToggle();
      this.restrictInputs(); // Restringir entrada de caracteres
      this.bindFieldEvents();
      this.bindFormSubmit();
      // NO sincronizar errores del backend al inicio para que el formulario esté limpio
      // this.syncBackendErrors();
      this.applyMobileOptimizations();
      this.addFieldAnimations();

      console.log('✅ Sistema de validación iniciado correctamente');
    }

    // ========================================================================
    // LIMPIAR FORMULARIO AL CARGAR LA PÁGINA
    // ========================================================================
    cleanFormOnLoad() {
      // Remover todas las clases de validación de los campos
      const allInputs = document.querySelectorAll('.form-control');
      allInputs.forEach(input => {
        input.classList.remove('is-valid', 'is-invalid');
      });

      // Ocultar todos los mensajes de feedback
      const feedbacks = document.querySelectorAll('.valid-feedback, .invalid-feedback');
      feedbacks.forEach(fb => {
        fb.style.display = 'none';
      });

      // Asegurar que el foco esté en el campo de documento
      setTimeout(() => {
        const documentoField = document.getElementById('id_documento');
        if (documentoField) {
          documentoField.focus();
        }
      }, 100);

      console.log('✅ Formulario limpiado - estado inicial');
    }

    // ========================================================================
    // INICIALIZACIÓN DE TOASTS BOOTSTRAP 5
    // ========================================================================
    initializeToasts() {
      console.log('🎨 Inicializando sistema de toasts...');

      // Verificar que Bootstrap esté disponible
      if (typeof bootstrap === 'undefined') {
        console.error('❌ Bootstrap no está cargado. Los toasts no funcionarán.');
        return;
      }

      const toastConfigs = {
        success: { delay: 9000, animation: true },
        error: { delay: 12000, animation: true },
        warning: { delay: 10000, animation: true }
      };

      let toastsInicializados = 0;

      Object.keys(toastConfigs).forEach(type => {
        const toastEl = document.getElementById(`${type}Toast`);

        if (toastEl) {
          try {
            this.toasts[type] = new bootstrap.Toast(toastEl, toastConfigs[type]);
            toastsInicializados++;
            console.log(`✅ Toast ${type} inicializado correctamente`);
          } catch (error) {
            console.error(`❌ Error al inicializar toast ${type}:`, error);
          }
        } else {
          console.warn(`⚠️ No se encontró el elemento HTML: ${type}Toast`);
        }
      });

      console.log(`📊 Total de toasts inicializados: ${toastsInicializados}/3`);
    }

    /**
     * Mostrar toast según tipo con animación
     */
    showToast(type, message) {
      console.log(`🔔 Intentando mostrar toast: tipo="${type}", mensaje="${message}"`);

      const messageEl = document.getElementById(`${type}ToastMessage`);
      const toastInstance = this.toasts[type];

      if (!messageEl) {
        console.error(`❌ No se encontró el elemento de mensaje: ${type}ToastMessage`);
        return;
      }

      if (!toastInstance) {
        console.error(`❌ No se encontró la instancia del toast: ${type}`);
        console.log('Toasts disponibles:', Object.keys(this.toasts));
        return;
      }

      // Actualizar el mensaje
      messageEl.textContent = message;
      console.log(`✅ Mensaje actualizado en ${type}ToastMessage`);

      // Mostrar el toast
      try {
        toastInstance.show();
        console.log(`📢 Toast ${type} mostrado exitosamente`);
      } catch (error) {
        console.error(`❌ Error al mostrar toast: ${error.message}`);
      }
    }

    // ========================================================================
    // CONVERSIÓN DE MENSAJES DJANGO A TOASTS
    // ========================================================================
    convertDjangoMessages() {
      const djangoMessages = document.getElementById('django-messages');
      if (!djangoMessages) {
        console.log('ℹ️ No hay mensajes de Django para mostrar');
        return;
      }

      const messages = djangoMessages.querySelectorAll('[data-message-level]');
      console.log(`📨 Procesando ${messages.length} mensajes de Django`);

      messages.forEach(msg => {
        const level = msg.getAttribute('data-message-level');
        const text = msg.getAttribute('data-message-text');

        console.log(`  📋 Mensaje recibido: level="${level}", text="${text}"`);

        // Mapear niveles de Django a tipos de toast
        if (level.includes('level-success')) {
          this.showToast('success', text);
        } else if (level.includes('level-error')) {
          this.showToast('error', text);
        } else if (level.includes('level-warning')) {
          this.showToast('warning', text);
        } else if (level.includes('success')) {
          this.showToast('success', text);
        } else if (level.includes('error') || level.includes('danger')) {
          this.showToast('error', text);
        } else if (level.includes('warning') || level.includes('info')) {
          this.showToast('warning', text);
        }
      });
    }

    // ========================================================================
    // TOGGLE MOSTRAR/OCULTAR CONTRASEÑA
    // ========================================================================
    initializePasswordToggle() {
      const buttons = document.querySelectorAll('.toggle-password[data-target]');
      buttons.forEach(btn => {
        const targetId = btn.getAttribute('data-target');
        const input = document.getElementById(targetId);
        if (!input) return;

        btn.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();

          const isText = input.getAttribute('type') === 'text';
          input.setAttribute('type', isText ? 'password' : 'text');

          // Cambiar el ícono del botón sin afectar su posición
          const icon = btn.querySelector('i');
          if (icon) {
            icon.className = isText ? 'bi bi-eye' : 'bi bi-eye-slash';
          }

          // Micro animación de opacidad para feedback visual
          btn.style.opacity = '0.6';
          setTimeout(() => {
            btn.style.opacity = '1';
          }, 100);
        });
      });
      console.log('✅ Toggles de contraseña inicializados');
    }

    // ========================================================================
    // RESTRINGIR ENTRADA DE CARACTERES
    // ========================================================================
    restrictInputs() {
      // Documento: solo números
      const documentoField = document.getElementById('id_documento');
      if (documentoField) {
        documentoField.addEventListener('keypress', (e) => {
          // Permitir solo números
          if (!/[0-9]/.test(e.key)) {
            e.preventDefault();
          }
        });
        documentoField.addEventListener('paste', (e) => {
          e.preventDefault();
          const pastedText = (e.clipboardData || window.clipboardData).getData('text');
          const numbersOnly = pastedText.replace(/\D/g, '');
          documentoField.value = numbersOnly.substring(0, 10);
        });
      }

      // Nombre y Apellido: solo letras y espacios
      const nameFields = ['id_first_name', 'id_last_name'];
      nameFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
          field.addEventListener('keypress', (e) => {
            // Permitir solo letras (incluye acentos y ñ) y espacios
            if (!/[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/.test(e.key)) {
              e.preventDefault();
            }
          });
          field.addEventListener('paste', (e) => {
            e.preventDefault();
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const lettersOnly = pastedText.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
            field.value = lettersOnly;
          });
        }
      });

      console.log('✅ Restricciones de entrada aplicadas');
    }

    // ========================================================================
    // VALIDADORES POR CAMPO
    // ========================================================================
    getValidators() {
      return {
        id_documento: (value) => {
          const trimmed = value.trim();
          const valid = /^\d{10}$/.test(trimmed);
          return {
            valid: valid,
            message: valid ? 'Documento válido' : 'El documento debe tener exactamente 10 dígitos numéricos'
          };
        },

        id_email: (value) => {
          const trimmed = value.trim();
          const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed);
          return {
            valid: valid,
            message: valid ? 'Correo válido' : 'Ingresa un correo válido'
          };
        },

        id_username: (value) => {
          const trimmed = value.trim();
          const valid = trimmed.length >= 4 && /^[a-zA-Z0-9_-]+$/.test(trimmed);
          let message = 'Usuario válido';

          if (trimmed.length < 4) {
            message = 'El usuario debe tener al menos 4 caracteres';
          } else if (!/^[a-zA-Z0-9_-]+$/.test(trimmed)) {
            message = 'Solo letras, números, guiones (-) y guiones bajos (_)';
          }

          return {
            valid: valid,
            message: message
          };
        },

        id_first_name: (value) => {
          const trimmed = value.trim();
          const valid = trimmed.length > 0 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(trimmed);
          return {
            valid: valid,
            message: valid ? 'Nombre válido' : 'El nombre solo puede contener letras'
          };
        },

        id_last_name: (value) => {
          const trimmed = value.trim();
          const valid = trimmed.length > 0 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(trimmed);
          return {
            valid: valid,
            message: valid ? 'Apellido válido' : 'El apellido solo puede contener letras'
          };
        },

        id_password1: (value) => {
          const result = this.checkPasswordRequirements(value);
          return {
            valid: result.allValid,
            message: result.allValid ? 'Contraseña válida' : 'La contraseña no cumple todos los requisitos'
          };
        },

        id_password2: (value) => {
          const pwd1 = document.getElementById('id_password1');
          const valid = pwd1 && value === pwd1.value && value.length > 0;
          return {
            valid: valid,
            message: valid ? 'Las contraseñas coinciden' : 'Las contraseñas no coinciden'
          };
        }
      };
    }

    /**
     * Validar campo y aplicar clases Bootstrap con animación
     */
    validateField(input) {
      const validators = this.getValidators();
      const validator = validators[input.id];

      if (!validator) return true;

      const result = validator(input.value);

      // Remover clases previas
      input.classList.remove('is-valid', 'is-invalid');

      // Actualizar feedback
      const parent = input.closest('.form-floating') || input.closest('.form-group');
      if (parent) {
        const invalidFeedback = parent.querySelector('.invalid-feedback');
        const validFeedback = parent.querySelector('.valid-feedback');

        // SOLO mostrar validaciones si el campo tiene contenido
        // Esto evita que aparezcan errores al cargar la página
        if (input.value.trim().length > 0) {
          // Aplicar clase con animación
          input.classList.add(result.valid ? 'is-valid' : 'is-invalid');

          // Actualizar mensajes
          if (result.valid && validFeedback) {
            validFeedback.textContent = result.message;
          } else if (!result.valid && invalidFeedback) {
            invalidFeedback.textContent = result.message;
          }

          // Animación de shake si es inválido
          if (!result.valid) {
            this.shakeElement(input);
          }
        }
      }

      return result.valid;
    }

    /**
     * Animación de shake para campos inválidos
     */
    shakeElement(element) {
      element.style.animation = 'none';
      setTimeout(() => {
        element.style.animation = 'shake 0.5s';
      }, 10);
    }

    // ========================================================================
    // CHECKLIST Y PROGRESS DE CONTRASEÑA
    // ========================================================================
    checkPasswordRequirements(password) {
      let fulfilled = 0;
      const total = Object.keys(this.passwordRequirements).length;

      Object.entries(this.passwordRequirements).forEach(([, req]) => {
        const met = req.regex.test(password);
        const el = document.getElementById(req.element);

        if (el) {
          const icon = el.querySelector('i');
          if (icon) {
            // Animación de transición
            icon.style.transition = 'all 0.3s ease';

            if (met) {
              icon.className = 'bi bi-check-circle-fill text-success';
              el.classList.add('text-success');
              el.classList.remove('text-muted');
              fulfilled++;
            } else {
              icon.className = 'bi bi-circle text-muted';
              el.classList.remove('text-success');
              el.classList.add('text-muted');
            }
          }
        }
      });

      return {
        fulfilled: fulfilled,
        total: total,
        allValid: fulfilled === total
      };
    }

    updatePasswordProgress(password) {
      const result = this.checkPasswordRequirements(password);
      const progressBar = document.getElementById('password-progress');
      const strengthText = document.getElementById('password-strength-text');

      if (!progressBar) return;

      const percent = (result.fulfilled / result.total) * 100;

      // Animación suave de la barra
      progressBar.style.transition = 'width 0.3s ease, background-color 0.3s ease';
      progressBar.style.width = percent + '%';
      progressBar.setAttribute('aria-valuenow', percent);

      // Cambiar color según progreso con animación
      progressBar.className = 'progress-bar';

      let strengthLabel = 'Sin contraseña';

      if (percent === 0) {
        progressBar.classList.add('bg-secondary');
        strengthLabel = 'Sin contraseña';
      } else if (percent < 40) {
        progressBar.classList.add('bg-danger');
        strengthLabel = 'Muy débil';
      } else if (percent < 60) {
        progressBar.classList.add('bg-warning');
        strengthLabel = 'Débil';
      } else if (percent < 80) {
        progressBar.classList.add('bg-info');
        strengthLabel = 'Aceptable';
      } else if (percent < 100) {
        progressBar.classList.add('bg-primary');
        strengthLabel = 'Buena';
      } else {
        progressBar.classList.add('bg-success');
        strengthLabel = '¡Excelente!';
      }

      // Actualizar texto de fortaleza
      if (strengthText) {
        strengthText.textContent = strengthLabel;
      }

      // Actualizar visually-hidden para lectores de pantalla
      const srText = progressBar.querySelector('.visually-hidden');
      if (srText) {
        srText.textContent = `${percent}% completado - ${strengthLabel}`;
      }

      console.log(`🔐 Fortaleza de contraseña: ${percent}% - ${strengthLabel}`);
    }

    // ========================================================================
    // BIND DE EVENTOS EN CAMPOS
    // ========================================================================
    bindFieldEvents() {
      this.fieldsToValidate.forEach(id => {
        const el = document.getElementById(id);
        if (!el) {
          console.warn(`⚠️ Campo no encontrado: ${id}`);
          return;
        }

        // Agregar clase form-control si no la tiene
        if (!el.classList.contains('form-control')) {
          el.classList.add('form-control');
        }

        // Bandera para saber si el usuario ha empezado a escribir
        let hasInteracted = false;

        // Validar en tiempo real (input) - solo después de que el usuario empiece a escribir
        el.addEventListener('input', () => {
          hasInteracted = true;
          this.validateField(el);
        });

        // Validar al perder el foco (blur) - solo si ha interactuado y tiene contenido
        el.addEventListener('blur', () => {
          if (hasInteracted && el.value.trim().length > 0) {
            this.validateField(el);
          }
        });

        // Efecto de focus
        el.addEventListener('focus', () => {
          el.style.transform = 'scale(1.01)';
          el.style.transition = 'transform 0.2s ease';
        });

        el.addEventListener('blur', () => {
          el.style.transform = 'scale(1)';
        });
      });

      // Validación especial de contraseña
      const pwd1 = document.getElementById('id_password1');
      const pwd2 = document.getElementById('id_password2');

      if (pwd1) {
        pwd1.addEventListener('input', (e) => {
          this.updatePasswordProgress(e.target.value);
          this.validateField(pwd1);

          // Revalidar confirmación si ya tiene valor
          if (pwd2 && pwd2.value.length > 0) {
            this.validateField(pwd2);
          }
        });
      }

      if (pwd2) {
        pwd2.addEventListener('input', () => {
          this.validateField(pwd2);
        });
      }

      console.log('✅ Eventos de campos vinculados');
    }

    // ========================================================================
    // VALIDACIÓN AL ENVIAR FORMULARIO
    // ========================================================================
    bindFormSubmit() {
      const form = document.querySelector('form[method="post"]');
      if (!form) {
        console.warn('⚠️ Formulario no encontrado');
        return;
      }

      form.addEventListener('submit', (e) => {
        console.log('📝 Validando formulario antes de enviar...');

        let hasErrors = false;
        let firstInvalidField = null;
        const errors = [];

        // Validar TODOS los campos obligatorios (no solo que estén llenos, sino con formato correcto)
        this.fieldsToValidate.forEach(id => {
          const input = document.getElementById(id);
          if (input) {
            const isEmpty = !input.value || input.value.trim() === '';
            console.log(`Campo ${id}: ${isEmpty ? '❌ Vacío' : '✅ Tiene valor'} - Valor: "${input.value}"`);

            if (isEmpty) {
              hasErrors = true;
              input.classList.add('is-invalid');
              input.classList.remove('is-valid');
              errors.push(`${input.name || id}: Campo vacío`);
              console.log(`❌ ${id}: Vacío`);

              if (!firstInvalidField) {
                firstInvalidField = input;
              }
            } else {
              // Validar formato usando los validadores
              const isValid = this.validateField(input);
              if (!isValid) {
                hasErrors = true;
                errors.push(`${input.name || id}: Formato inválido`);
                console.log(`❌ ${id}: Formato inválido - "${input.value}"`);

                if (!firstInvalidField) {
                  firstInvalidField = input;
                }
              } else {
                console.log(`✅ ${id}: Válido - "${input.value}"`);
              }
            }
          }
        });

        if (hasErrors) {
          e.preventDefault();
          console.log('❌ FORMULARIO CON ERRORES - NO SE ENVIARÁ');
          console.log('Errores encontrados:', errors);

          this.showToast('warning', 'Por favor, corrige los campos marcados en rojo antes de continuar.');

          // Scroll al primer campo inválido
          if (firstInvalidField) {
            firstInvalidField.scrollIntoView({
              behavior: 'smooth',
              block: 'center'
            });

            setTimeout(() => {
              firstInvalidField.focus();
              this.shakeElement(firstInvalidField);
            }, 300);
          }
        } else {
          console.log('✅ FORMULARIO VÁLIDO - ENVIANDO AL SERVIDOR...');
          console.log('📤 Datos a enviar:');
          this.fieldsToValidate.forEach(id => {
            const input = document.getElementById(id);
            if (input && input.type !== 'password') {
              console.log(`  • ${id}: "${input.value}"`);
            }
          });
        }
      });

      console.log('✅ Validación de envío de formulario configurada');
    }

    // ========================================================================
    // SINCRONIZAR ERRORES DEL BACKEND
    // ========================================================================
    syncBackendErrors() {
      const fields = document.querySelectorAll('.form-floating, .form-group');
      let hasBackendErrors = false;

      fields.forEach(wrapper => {
        const input = wrapper.querySelector('input, select, textarea');
        const feedback = wrapper.querySelector('.invalid-feedback');

        if (input && feedback) {
          const backendError = feedback.textContent.trim();

          // Detectar si es un error real del backend (no un placeholder)
          const isPlaceholder = backendError.includes('debe tener exactamente') ||
                                backendError.includes('Ingresa un') ||
                                backendError.includes('es obligatorio') ||
                                backendError.includes('coinciden') ||
                                backendError.includes('válido') ||
                                backendError.includes('inválida') ||
                                backendError.length < 10;

          if (!isPlaceholder && backendError.length > 0) {
            input.classList.add('is-invalid');
            hasBackendErrors = true;
            console.log(`⚠️ Error del backend en ${input.id}: ${backendError}`);
          }
        }
      });

      if (hasBackendErrors) {
        this.showToast('error', 'Hay errores en el formulario. Por favor, revísalos.');
      }
    }

    // ========================================================================
    // MEJORAS MÓVILES
    // ========================================================================
    applyMobileOptimizations() {
      const inputs = document.querySelectorAll('input, select, textarea');
      inputs.forEach(el => {
        // Evitar zoom en iOS cuando se hace focus en inputs
        if (el.style.fontSize === '' || parseFloat(el.style.fontSize) < 16) {
          el.style.fontSize = '16px';
        }
      });
      console.log('✅ Optimizaciones móviles aplicadas');
    }

    // ========================================================================
    // ANIMACIONES ADICIONALES
    // ========================================================================
    addFieldAnimations() {
      // Agregar animación de shake CSS si no existe
      if (!document.getElementById('validation-animations')) {
        const style = document.createElement('style');
        style.id = 'validation-animations';
        style.textContent = `
          @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
          }
          
          .form-control.is-invalid {
            border-color: #dc3545 !important;
            box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
          }
          
          .form-control.is-valid {
            border-color: #28a745 !important;
            box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
          }
          
          .form-control:focus {
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
          }
          
          .progress-bar {
            transition: width 0.3s ease, background-color 0.3s ease;
          }
          
          .toggle-password {
            transition: transform 0.1s ease;
          }
          
          .password-requirements li {
            transition: color 0.3s ease;
          }
          
          .password-requirements li i {
            transition: all 0.3s ease;
          }
        `;
        document.head.appendChild(style);
        console.log('✅ Estilos de animación agregados');
      }
    }
  }

  // ============================================================================
  // INICIALIZACIÓN AUTOMÁTICA
  // ============================================================================
  function init() {
    console.log('🎨 Iniciando sistema de registro ARTES_Y_ESTILOS');

    // Verificar que Bootstrap esté disponible
    if (typeof bootstrap === 'undefined') {
      console.error('❌ Bootstrap 5 no está cargado. El sistema de validación no funcionará.');
      console.log('💡 Asegúrate de que Bootstrap 5 esté incluido en master.html');
      return;
    }

    // Crear e inicializar el validador
    const validator = new RegistroValidator();
    validator.initialize();
  }

  // Esperar a que el DOM esté completamente cargado
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

// ============================================================================
// SLIDESHOW DE FONDO ANIMADO
// ============================================================================
(function() {
  'use strict';

  function initBackgroundSlideshow() {
    const container = document.getElementById('bg-slideshow');
    if (!container) {
      console.warn('⚠️ Contenedor de slideshow no encontrado');
      return;
    }

    const slides = Array.from(container.querySelectorAll('.slide'));
    if (slides.length === 0) {
      console.warn('⚠️ No se encontraron slides');
      return;
    }

    let currentIndex = 0;

    const activateSlide = (index) => {
      slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
      });
    };

    // Activar el primer slide
    activateSlide(currentIndex);
    console.log('✅ Slideshow de fondo iniciado');

    // Cambiar slide cada 10 segundos
    setInterval(() => {
      currentIndex = (currentIndex + 1) % slides.length;
      activateSlide(currentIndex);
    }, 10000); // 10 segundos
  }

  // Inicializar slideshow cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBackgroundSlideshow);
  } else {
    initBackgroundSlideshow();
  }

})();

