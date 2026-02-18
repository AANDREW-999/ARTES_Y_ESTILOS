/**
 * LOGIN.JS - Sistema de validación y UX profesional con Bootstrap 5
 * Versión optimizada con toasts y feedback dinámico
 * @version 2.0
 * @date 2026-02-16
 */

(function() {
  'use strict';

  // ============================================================================
  // CLASE PRINCIPAL DE VALIDACIÓN DE LOGIN
  // ============================================================================
  class LoginValidator {
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
      console.log('🚀 Iniciando sistema de login...');

      // Verificar que Bootstrap esté disponible
      if (typeof bootstrap === 'undefined') {
        console.error('❌ Bootstrap no está cargado');
        return;
      }

      this.initializeToasts();
      this.convertDjangoMessages();
      this.initializePasswordToggle();
      this.addFormControls();
      this.bindFormValidation();
      this.initializeSlideshow();

      console.log('✅ Sistema de login iniciado correctamente');
    }

    // ========================================================================
    // INICIALIZACIÓN DE TOASTS BOOTSTRAP 5
    // ========================================================================
    initializeToasts() {
      console.log('🎨 Inicializando sistema de toasts...');

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
      console.log(`🔔 Mostrando toast: tipo="${type}", mensaje="${message}"`);

      const messageEl = document.getElementById(`${type}ToastMessage`);
      const toastInstance = this.toasts[type];

      if (!messageEl || !toastInstance) {
        console.error(`❌ No se encontró el toast: ${type}`);
        return;
      }

      messageEl.textContent = message;

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
      const button = document.querySelector('.toggle-password[data-target]');
      if (!button) {
        console.warn('⚠️ No se encontró botón toggle-password');
        return;
      }

      const targetId = button.getAttribute('data-target');
      const input = document.getElementById(targetId);

      if (!input) {
        console.warn(`⚠️ No se encontró input con id: ${targetId}`);
        return;
      }

      button.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();

        const isText = input.getAttribute('type') === 'text';
        input.setAttribute('type', isText ? 'password' : 'text');

        const icon = button.querySelector('i');
        if (icon) {
          icon.className = isText ? 'bi bi-eye' : 'bi bi-eye-slash';
        }

        // Micro animación de feedback
        button.style.opacity = '0.6';
        setTimeout(() => {
          button.style.opacity = '1';
        }, 100);
      });

      console.log('✅ Toggle de contraseña inicializado');
    }

    // ========================================================================
    // AGREGAR CLASES FORM-CONTROL Y PLACEHOLDERS
    // ========================================================================
    addFormControls() {
      const inputs = [
        { id: 'id_username', placeholder: 'Usuario o documento' },
        { id: 'id_password', placeholder: 'Ingrese su contraseña' }
      ];

      inputs.forEach(({ id, placeholder }) => {
        const input = document.getElementById(id);
        if (input) {
          if (!input.classList.contains('form-control')) {
            input.classList.add('form-control');
          }
          if (!input.placeholder) {
            input.placeholder = placeholder;
          }
        }
      });

      console.log('✅ Clases form-control agregadas');
    }

    // ========================================================================
    // VALIDACIÓN DE FORMULARIO
    // ========================================================================
    bindFormValidation() {
      const form = document.getElementById('loginForm');
      if (!form) {
        console.warn('⚠️ Formulario de login no encontrado');
        return;
      }

      // Validación en tiempo real
      const usernameInput = document.getElementById('id_username');
      const passwordInput = document.getElementById('id_password');

      [usernameInput, passwordInput].forEach(input => {
        if (!input) return;

        // Validar al escribir
        input.addEventListener('input', () => {
          this.validateField(input);
        });

        // Validar al perder foco
        input.addEventListener('blur', () => {
          if (input.value.trim().length > 0) {
            this.validateField(input);
          }
        });

        // Animación de focus
        input.addEventListener('focus', () => {
          input.style.transform = 'scale(1.01)';
          input.style.transition = 'transform 0.2s ease';
        });

        input.addEventListener('blur', () => {
          input.style.transform = 'scale(1)';
        });
      });

      // Validación al enviar
      form.addEventListener('submit', (e) => {
        console.log('📝 Validando formulario de login...');

        let hasErrors = false;
        const errors = [];

        // Validar campos obligatorios
        [usernameInput, passwordInput].forEach(input => {
          if (!input) return;

          const isEmpty = !input.value || input.value.trim() === '';

          if (isEmpty) {
            hasErrors = true;
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
            errors.push(input.id);
            console.log(`❌ ${input.id}: Campo vacío`);
          } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            console.log(`✅ ${input.id}: Válido`);
          }
        });

        if (hasErrors) {
          e.preventDefault();
          console.log('❌ FORMULARIO CON ERRORES - NO SE ENVIARÁ');

          this.showToast('warning', '⚠️ Por favor, completa todos los campos para iniciar sesión.');

          // Focus en el primer campo con error
          const firstInvalid = form.querySelector('.is-invalid');
          if (firstInvalid) {
            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => {
              firstInvalid.focus();
              this.shakeElement(firstInvalid);
            }, 300);
          }
        } else {
          console.log('✅ FORMULARIO VÁLIDO - ENVIANDO AL SERVIDOR...');
        }
      });

      console.log('✅ Validación de formulario configurada');
    }

    /**
     * Validar campo individual
     */
    validateField(input) {
      const value = input.value.trim();
      const isEmpty = value.length === 0;

      input.classList.remove('is-valid', 'is-invalid');

      if (value.length > 0) {
        if (isEmpty) {
          input.classList.add('is-invalid');
        } else {
          input.classList.add('is-valid');
        }
      }
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
    // SLIDESHOW DE FONDO
    // ========================================================================
    initializeSlideshow() {
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
      }, 10000);
    }
  }

  // ============================================================================
  // INICIALIZACIÓN AUTOMÁTICA
  // ============================================================================
  function init() {
    console.log('🎨 Iniciando sistema de login ARTES_Y_ESTILOS');

    // Verificar que Bootstrap esté disponible
    if (typeof bootstrap === 'undefined') {
      console.error('❌ Bootstrap 5 no está cargado. El sistema de login no funcionará.');
      return;
    }

    // Crear e inicializar el validador
    const validator = new LoginValidator();
    validator.initialize();
  }

  // Esperar a que el DOM esté completamente cargado
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
