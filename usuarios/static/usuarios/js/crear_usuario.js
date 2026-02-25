/**
 * CREAR_USUARIO.JS - Sistema de validación para crear usuarios desde el panel admin
 * Versión optimizada con animaciones y feedback dinámico
 * Basado en registro.js
 * @version 1.0
 * @date 2026-02-23
 */

(function() {
  'use strict';

  // ============================================================================
  // CLASE PRINCIPAL DE VALIDACIÓN
  // ============================================================================
  class CrearUsuarioValidator {
    constructor() {
      this.toasts = {
        success: null,
        error: null,
        warning: null,
        info: null
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
      console.log('🚀 Iniciando sistema de validación de crear usuario...');

      // Verificar que Bootstrap esté disponible
      if (typeof bootstrap === 'undefined') {
        console.error('❌ Bootstrap no está cargado');
        return;
      }

      this.cleanFormOnLoad();
      this.initializeToasts();
      this.convertDjangoMessages();
      this.initializePasswordToggle();
      this.restrictInputs();
      this.bindFieldEvents();
      this.bindFormSubmit();
      this.applyMobileOptimizations();
      this.addFieldAnimations();
      this.checkPerfilDataOnCollapse();

      console.log('✅ Sistema de validación iniciado correctamente');
    }

    // ========================================================================
    // LIMPIAR FORMULARIO AL CARGAR LA PÁGINA
    // ========================================================================
    cleanFormOnLoad() {
      const allInputs = document.querySelectorAll('.form-control');
      allInputs.forEach(input => {
        input.classList.remove('is-valid', 'is-invalid');
      });

      const feedbacks = document.querySelectorAll('.valid-feedback, .invalid-feedback');
      feedbacks.forEach(fb => {
        fb.style.display = 'none';
      });

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

      if (typeof bootstrap === 'undefined') {
        console.error('❌ Bootstrap no está cargado. Los toasts no funcionarán.');
        return;
      }

      const toastConfigs = {
        success: { delay: 9000, animation: true },
        error: { delay: 12000, animation: true },
        warning: { delay: 10000, animation: true },
        info: { delay: 15000, animation: true }
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

      console.log(`📊 Total de toasts inicializados: ${toastsInicializados}/4`);
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

      messageEl.textContent = message;
      console.log(`✅ Mensaje actualizado en ${type}ToastMessage`);

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

        if (level.includes('level-success') || level.includes('success')) {
          this.showToast('success', text);
        } else if (level.includes('level-error') || level.includes('error') || level.includes('danger')) {
          this.showToast('error', text);
        } else if (level.includes('level-warning') || level.includes('warning') || level.includes('info')) {
          this.showToast('warning', text);
        }
      });

      console.log('✅ Mensajes de Django convertidos a toasts');
    }

    // ========================================================================
    // TOGGLE DE CONTRASEÑA
    // ========================================================================
    initializePasswordToggle() {
      const toggleButtons = document.querySelectorAll('.toggle-password');

      toggleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
          const targetId = btn.getAttribute('data-target');
          const input = document.getElementById(targetId);
          const icon = btn.querySelector('i');

          if (input && icon) {
            if (input.type === 'password') {
              input.type = 'text';
              icon.classList.remove('bi-eye');
              icon.classList.add('bi-eye-slash');
            } else {
              input.type = 'password';
              icon.classList.remove('bi-eye-slash');
              icon.classList.add('bi-eye');
            }

            btn.style.transform = 'scale(0.9)';
            setTimeout(() => {
              btn.style.transform = 'scale(1)';
            }, 100);
          }
        });
      });

      console.log(`✅ ${toggleButtons.length} botones de toggle de contraseña inicializados`);
    }

    // ========================================================================
    // RESTRICCIONES DE ENTRADA
    // ========================================================================
    restrictInputs() {
      const documentoField = document.getElementById('id_documento');
      if (documentoField) {
        documentoField.addEventListener('keypress', (e) => {
          if (!/\d/.test(e.key)) {
            e.preventDefault();
          }
        });
        documentoField.addEventListener('input', (e) => {
          e.target.value = e.target.value.replace(/\D/g, '').substring(0, 10);
        });
        documentoField.addEventListener('paste', (e) => {
          e.preventDefault();
          const pastedText = (e.clipboardData || window.clipboardData).getData('text');
          const numbersOnly = pastedText.replace(/\D/g, '');
          documentoField.value = numbersOnly.substring(0, 10);
        });
      }

      const nameFields = ['id_first_name', 'id_last_name'];
      nameFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
          field.addEventListener('keypress', (e) => {
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
    validateField(input, forceValidation = false) {
      const validators = this.getValidators();
      const validator = validators[input.id];

      if (!validator) return true;

      const result = validator(input.value);
      const hasContent = input.value.trim().length > 0;

      // Limpiar estados previos
      input.classList.remove('is-valid', 'is-invalid');

      const parent = input.closest('.form-floating') || input.closest('.form-group') || input.parentElement;
      if (!parent) return result.valid;

      const invalidFeedback = parent.querySelector('.invalid-feedback');
      const validFeedback = parent.querySelector('.valid-feedback');

      // Ocultar todos los feedbacks primero
      if (invalidFeedback) invalidFeedback.style.display = 'none';
      if (validFeedback) validFeedback.style.display = 'none';

      // Solo mostrar validaciones si:
      // 1. El campo tiene contenido O
      // 2. Se fuerza la validación (submit del formulario)
      if (hasContent || forceValidation) {
        if (result.valid && hasContent) {
          input.classList.add('is-valid');
          if (validFeedback) {
            validFeedback.innerHTML = `<i class="bi bi-check-circle me-1"></i>${result.message}`;
            validFeedback.style.display = 'block';
          }
        } else if (!result.valid) {
          input.classList.add('is-invalid');
          if (invalidFeedback) {
            invalidFeedback.innerHTML = `<i class="bi bi-exclamation-circle me-1"></i>${result.message}`;
            invalidFeedback.style.display = 'block';
          }
          if (forceValidation) {
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

      progressBar.style.transition = 'width 0.3s ease, background-color 0.3s ease';
      progressBar.style.width = percent + '%';
      progressBar.setAttribute('aria-valuenow', percent);

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

      if (strengthText) {
        strengthText.textContent = strengthLabel;
      }

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
      // Map para rastrear si el usuario ha interactuado con cada campo
      const interactedFields = new Map();

      this.fieldsToValidate.forEach(id => {
        const el = document.getElementById(id);
        if (!el) {
          console.warn(`⚠️ Campo no encontrado: ${id}`);
          return;
        }

        if (!el.classList.contains('form-control')) {
          el.classList.add('form-control');
        }

        // Marcar como interactuado cuando el usuario empieza a escribir
        el.addEventListener('input', () => {
          interactedFields.set(id, true);
          this.validateField(el, false);
        });

        // Validar al perder el foco solo si ha interactuado
        el.addEventListener('blur', () => {
          if (interactedFields.get(id) && el.value.trim().length > 0) {
            this.validateField(el, false);
          }
        });

        // Animación de focus
        el.addEventListener('focus', () => {
          el.style.transform = 'scale(1.01)';
          el.style.transition = 'transform 0.2s ease';
        });

        el.addEventListener('blur', () => {
          el.style.transform = 'scale(1)';
        });
      });

      // Eventos especiales para contraseñas
      const pwd1 = document.getElementById('id_password1');
      const pwd2 = document.getElementById('id_password2');

      if (pwd1) {
        pwd1.addEventListener('input', (e) => {
          interactedFields.set('id_password1', true);
          this.updatePasswordProgress(e.target.value);
          this.validateField(pwd1, false);

          // Si pwd2 ya tiene contenido, revalidarlo
          if (pwd2 && pwd2.value.length > 0 && interactedFields.get('id_password2')) {
            this.validateField(pwd2, false);
          }
        });
      }

      if (pwd2) {
        pwd2.addEventListener('input', () => {
          interactedFields.set('id_password2', true);
          this.validateField(pwd2, false);
        });
      }

      console.log('✅ Eventos de campos vinculados');
    }

    // ========================================================================
    // VALIDACIÓN AL ENVIAR FORMULARIO
    // ========================================================================
    bindFormSubmit() {
      const form = document.getElementById('crearUsuarioForm');
      if (!form) {
        console.warn('⚠️ Formulario no encontrado');
        return;
      }

      form.addEventListener('submit', (e) => {
        console.log('📝 Validando formulario antes de enviar...');

        let hasErrors = false;
        let firstInvalidField = null;
        const errors = [];

        this.fieldsToValidate.forEach(id => {
          const input = document.getElementById(id);
          if (input) {
            const isEmpty = !input.value || input.value.trim() === '';

            if (isEmpty) {
              hasErrors = true;
              input.classList.add('is-invalid');
              input.classList.remove('is-valid');

              const parent = input.closest('.form-floating') || input.closest('.form-group') || input.parentElement;
              const invalidFeedback = parent ? parent.querySelector('.invalid-feedback') : null;
              if (invalidFeedback) {
                invalidFeedback.innerHTML = '<i class="bi bi-exclamation-circle me-1"></i>Este campo es obligatorio';
                invalidFeedback.style.display = 'block';
              }

              errors.push(`${input.name || id}: Campo vacío`);
              console.log(`❌ ${id}: Vacío`);

              if (!firstInvalidField) {
                firstInvalidField = input;
              }
            } else {
              // Forzar validación en submit
              const isValid = this.validateField(input, true);
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
    // VERIFICAR DATOS DE PERFIL OPCIONALES
    // ========================================================================
    checkPerfilDataOnCollapse() {
      const collapseElement = document.getElementById('perfilCollapse');
      if (!collapseElement) {
        console.log('⚠️ Collapse de perfil no encontrado');
        return;
      }

      const form = document.getElementById('crearUsuarioForm');
      if (!form) return;

      form.addEventListener('submit', (e) => {
        // Verificar si los campos opcionales están vacíos
        const telefono = document.getElementById('id_telefono');
        const fecha_nacimiento = document.getElementById('id_fecha_nacimiento');
        const direccion = document.getElementById('id_direccion');
        const foto_perfil = document.getElementById('id_foto_perfil');

        const perfilVacio = (!telefono || !telefono.value.trim()) &&
                           (!fecha_nacimiento || !fecha_nacimiento.value.trim()) &&
                           (!direccion || !direccion.value.trim()) &&
                           (!foto_perfil || !foto_perfil.value);

        // Si el perfil está vacío y no hay errores de validación, mostrar toast informativo
        if (perfilVacio && !e.defaultPrevented) {
          // Esperar un momento y luego mostrar el toast
          setTimeout(() => {
            this.showToast('info', 'Recuerda que el usuario puede completar su perfil (teléfono, fecha de nacimiento, dirección y foto) después del primer inicio de sesión.');
          }, 500);
        }
      });

      console.log('✅ Verificación de datos de perfil configurada');
    }

    // ========================================================================
    // MEJORAS MÓVILES
    // ========================================================================
    applyMobileOptimizations() {
      const inputs = document.querySelectorAll('input, select, textarea');
      inputs.forEach(el => {
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
    console.log('🎨 Iniciando sistema de crear usuario ARTES_Y_ESTILOS');

    if (typeof bootstrap === 'undefined') {
      console.error('❌ Bootstrap 5 no está cargado. El sistema de validación no funcionará.');
      return;
    }

    const validator = new CrearUsuarioValidator();
    validator.initialize();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

