/**
 * CONFIRMAR_PASSWORD.JS - Validación de formulario de nueva contraseña
 * Versión optimizada con Bootstrap 5, checklist y barra de progreso
 * @version 1.0
 * @date 2026-02-17
 */

(function() {
  'use strict';

  // ============================================================================
  // CLASE PRINCIPAL DE VALIDACIÓN
  // ============================================================================
  class ConfirmarPasswordValidator {
    constructor() {
      this.toasts = {
        success: null,
        error: null,
        warning: null
      };

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
      console.log('🚀 Iniciando validación de nueva contraseña...');

      if (typeof bootstrap === 'undefined') {
        console.error('❌ Bootstrap no está cargado');
        return;
      }

      this.initializeToasts();
      this.convertDjangoMessages();
      this.initializePasswordToggle();
      this.bindFieldEvents();
      this.bindFormSubmit();
      this.addFieldAnimations();

      console.log('✅ Sistema de validación iniciado correctamente');
    }

    // ========================================================================
    // INICIALIZACIÓN DE TOASTS BOOTSTRAP 5
    // ========================================================================
    initializeToasts() {
      const toastConfigs = {
        success: { delay: 9000, animation: true },
        error: { delay: 12000, animation: true },
        warning: { delay: 10000, animation: true }
      };

      Object.keys(toastConfigs).forEach(type => {
        const toastEl = document.getElementById(`${type}Toast`);
        if (toastEl) {
          this.toasts[type] = new bootstrap.Toast(toastEl, toastConfigs[type]);
        }
      });
    }

    showToast(type, message) {
      const messageEl = document.getElementById(`${type}ToastMessage`);
      const toastInstance = this.toasts[type];

      if (messageEl && toastInstance) {
        messageEl.textContent = message;
        toastInstance.show();
      }
    }

    // ========================================================================
    // CONVERSIÓN DE MENSAJES DJANGO A TOASTS
    // ========================================================================
    convertDjangoMessages() {
      const djangoMessages = document.getElementById('django-messages');
      if (!djangoMessages) return;

      const messages = djangoMessages.querySelectorAll('[data-message-level]');
      messages.forEach(msg => {
        const level = msg.getAttribute('data-message-level');
        const text = msg.getAttribute('data-message-text');

        if (level.includes('success')) {
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

          const icon = btn.querySelector('i');
          if (icon) {
            icon.className = isText ? 'bi bi-eye' : 'bi bi-eye-slash';
          }

          btn.style.opacity = '0.6';
          setTimeout(() => {
            btn.style.opacity = '1';
          }, 100);
        });
      });
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

      return result;
    }

    // ========================================================================
    // VALIDADORES
    // ========================================================================
    validatePassword(input) {
      const result = this.updatePasswordProgress(input.value);

      input.classList.remove('is-valid', 'is-invalid');

      if (input.value.length > 0) {
        input.classList.add(result.allValid ? 'is-valid' : 'is-invalid');
      }

      return result.allValid;
    }

    validatePasswordConfirm(input) {
      const pwd1 = document.getElementById('id_new_password1');
      const valid = pwd1 && input.value === pwd1.value && input.value.length > 0;

      input.classList.remove('is-valid', 'is-invalid');

      if (input.value.length > 0) {
        input.classList.add(valid ? 'is-valid' : 'is-invalid');

        if (!valid) {
          this.shakeElement(input);
        }
      }

      return valid;
    }

    shakeElement(element) {
      element.style.animation = 'none';
      setTimeout(() => {
        element.style.animation = 'shake 0.5s';
      }, 10);
    }

    // ========================================================================
    // BIND DE EVENTOS EN CAMPOS
    // ========================================================================
    bindFieldEvents() {
      const pwd1 = document.getElementById('id_new_password1');
      const pwd2 = document.getElementById('id_new_password2');

      if (pwd1) {
        if (!pwd1.classList.contains('form-control')) {
          pwd1.classList.add('form-control');
        }

        pwd1.addEventListener('input', () => {
          this.validatePassword(pwd1);

          // Revalidar confirmación si ya tiene valor
          if (pwd2 && pwd2.value.length > 0) {
            this.validatePasswordConfirm(pwd2);
          }
        });

        pwd1.addEventListener('focus', () => {
          pwd1.style.transform = 'scale(1.01)';
          pwd1.style.transition = 'transform 0.2s ease';
        });

        pwd1.addEventListener('blur', () => {
          pwd1.style.transform = 'scale(1)';
        });
      }

      if (pwd2) {
        if (!pwd2.classList.contains('form-control')) {
          pwd2.classList.add('form-control');
        }

        pwd2.addEventListener('input', () => {
          this.validatePasswordConfirm(pwd2);
        });

        pwd2.addEventListener('focus', () => {
          pwd2.style.transform = 'scale(1.01)';
          pwd2.style.transition = 'transform 0.2s ease';
        });

        pwd2.addEventListener('blur', () => {
          pwd2.style.transform = 'scale(1)';
        });
      }
    }

    // ========================================================================
    // VALIDACIÓN AL ENVIAR FORMULARIO
    // ========================================================================
    bindFormSubmit() {
      const form = document.getElementById('resetPasswordForm');
      if (!form) return;

      form.addEventListener('submit', (e) => {
        const pwd1 = document.getElementById('id_new_password1');
        const pwd2 = document.getElementById('id_new_password2');

        if (!pwd1 || !pwd2) {
          e.preventDefault();
          this.showToast('error', 'Error en el formulario. Recarga la página.');
          return;
        }

        let hasErrors = false;

        // Validar primera contraseña
        if (pwd1.value.trim() === '') {
          hasErrors = true;
          pwd1.classList.add('is-invalid');
        } else if (!this.validatePassword(pwd1)) {
          hasErrors = true;
        }

        // Validar confirmación
        if (pwd2.value.trim() === '') {
          hasErrors = true;
          pwd2.classList.add('is-invalid');
        } else if (!this.validatePasswordConfirm(pwd2)) {
          hasErrors = true;
        }

        if (hasErrors) {
          e.preventDefault();
          this.showToast('error', 'Por favor, corrige los campos marcados en rojo.');

          if (pwd1.value.trim() === '') {
            pwd1.focus();
          } else if (pwd2.value.trim() === '') {
            pwd2.focus();
          }
        } else {
          console.log('✅ Formulario válido - Guardando nueva contraseña...');
        }
      });
    }

    // ========================================================================
    // ANIMACIONES
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
          
          .progress-bar {
            transition: width 0.3s ease, background-color 0.3s ease;
          }
          
          .password-requirements li {
            transition: color 0.3s ease;
          }
          
          .password-requirements li i {
            transition: all 0.3s ease;
          }
        `;
        document.head.appendChild(style);
      }
    }
  }

  // ============================================================================
  // INICIALIZACIÓN AUTOMÁTICA
  // ============================================================================
  function init() {
    const validator = new ConfirmarPasswordValidator();
    validator.initialize();
  }

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
    if (!container) return;

    const slides = Array.from(container.querySelectorAll('.slide'));
    if (slides.length === 0) return;

    let currentIndex = 0;

    const activateSlide = (index) => {
      slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
      });
    };

    activateSlide(currentIndex);

    setInterval(() => {
      currentIndex = (currentIndex + 1) % slides.length;
      activateSlide(currentIndex);
    }, 10000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBackgroundSlideshow);
  } else {
    initBackgroundSlideshow();
  }

})();

