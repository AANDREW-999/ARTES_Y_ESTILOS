/**
 * RECUPERAR_PASSWORD.JS - Validación de formulario de recuperación de contraseña
 * Versión optimizada con Bootstrap 5 y validación en tiempo real
 * @version 1.0
 * @date 2026-02-17
 */

(function() {
  'use strict';

  // ============================================================================
  // CLASE PRINCIPAL DE VALIDACIÓN
  // ============================================================================
  class RecuperarPasswordValidator {
    constructor() {
      this.toasts = {
        success: null,
        error: null,
        warning: null
      };
    }

    // ========================================================================
    // INICIALIZACIÓN PRINCIPAL
    // ========================================================================
    initialize() {
      console.log('🚀 Iniciando validación de recuperación de contraseña...');

      if (typeof bootstrap === 'undefined') {
        console.error('❌ Bootstrap no está cargado');
        return;
      }

      this.initializeToasts();
      this.convertDjangoMessages();
      this.bindFieldEvents();
      this.bindFormSubmit();

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
    // VALIDACIÓN DE EMAIL
    // ========================================================================
    validateEmail(input) {
      const email = input.value.trim();
      const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

      input.classList.remove('is-valid', 'is-invalid');

      if (email.length > 0) {
        input.classList.add(isValid ? 'is-valid' : 'is-invalid');
      }

      return isValid;
    }

    // ========================================================================
    // BIND DE EVENTOS EN CAMPOS
    // ========================================================================
    bindFieldEvents() {
      const emailField = document.getElementById('id_email');
      if (!emailField) return;

      // Agregar clase form-control
      if (!emailField.classList.contains('form-control')) {
        emailField.classList.add('form-control');
      }

      // Validar en tiempo real
      emailField.addEventListener('input', () => {
        this.validateEmail(emailField);
      });

      emailField.addEventListener('blur', () => {
        if (emailField.value.trim().length > 0) {
          this.validateEmail(emailField);
        }
      });

      // Efecto de focus
      emailField.addEventListener('focus', () => {
        emailField.style.transform = 'scale(1.01)';
        emailField.style.transition = 'transform 0.2s ease';
      });

      emailField.addEventListener('blur', () => {
        emailField.style.transform = 'scale(1)';
      });
    }

    // ========================================================================
    // VALIDACIÓN AL ENVIAR FORMULARIO
    // ========================================================================
    bindFormSubmit() {
      const form = document.getElementById('recuperarForm');
      if (!form) return;

      form.addEventListener('submit', (e) => {
        const emailField = document.getElementById('id_email');

        if (!emailField) {
          e.preventDefault();
          this.showToast('error', 'Error en el formulario. Recarga la página.');
          return;
        }

        const email = emailField.value.trim();

        if (email === '') {
          e.preventDefault();
          emailField.classList.add('is-invalid');
          this.showToast('warning', 'Por favor, ingresa tu correo electrónico.');
          emailField.focus();
          return;
        }

        if (!this.validateEmail(emailField)) {
          e.preventDefault();
          this.showToast('error', 'Por favor, ingresa un correo electrónico válido.');
          emailField.focus();
          return;
        }

        console.log('✅ Formulario válido - Enviando solicitud...');
      });
    }
  }

  // ============================================================================
  // INICIALIZACIÓN AUTOMÁTICA
  // ============================================================================
  function init() {
    const validator = new RecuperarPasswordValidator();
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

