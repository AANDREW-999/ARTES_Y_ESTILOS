/**
 * registro.js — Artes & Estilos
 * Validación en tiempo real + Bootstrap 5 + Django 4.2
 *
 * CORRECCIONES v4.1 (sobre v3.0 real):
 *  BUG 1 — Eliminados listeners duplicados en password1
 *  BUG 2 — cleanFormOnLoad NO borra errores del backend
 *  BUG 3 — validateField siempre retorna boolean explícito
 *  BUG 4 — shakeElement con reflow forzado (compatible Safari)
 *  BUG 5 — colores de validación compatibles con auth.css v2.0
 */

(function () {
  'use strict';

  /* ─────────────────────────────────────────────────────────── */
  class RegistroValidator {

    constructor() {
      this.toasts = { success: null, error: null, warning: null };

      this.fieldsToValidate = [
        'id_documento',
        'id_email',
        'id_username',
        'id_first_name',
        'id_last_name',
        'id_password1',
        'id_password2',
      ];

      this.passwordRequirements = {
        length:    { regex: /.{8,}/,                                    element: 'req-length'    },
        lowercase: { regex: /[a-z]/,                                    element: 'req-lowercase' },
        uppercase: { regex: /[A-Z]/,                                    element: 'req-uppercase' },
        number:    { regex: /[0-9]/,                                    element: 'req-number'    },
        special:   { regex: /[!@#$%^&*()\-_=+[\]{};':",.<>/?\\|`~ ]/,  element: 'req-special'   },
      };
    }

    /* ── Inicialización ──────────────────────────────────────── */
    initialize() {
      if (typeof bootstrap === 'undefined') {
        console.error('[Registro] Bootstrap no disponible.');
        return;
      }

      // FIX BUG 2: primero detectar si hay errores del backend,
      // LUEGO limpiar solo lo que sea seguro
      this.syncBackendState();
      this.initializeToasts();
      this.convertDjangoMessages();
      this.initializePasswordToggle();
      this.restrictInputs();
      this.bindFieldEvents();   // FIX BUG 1: password1 solo aquí
      this.bindFormSubmit();
      this.applyMobileOptimizations();
    }

    /* ── FIX BUG 2: syncBackendState en lugar de cleanFormOnLoad ─
       Preserva errores que Django pintó en el POST fallido.
       Solo limpia is-valid residuales de campos sin valor.        */
    syncBackendState() {
      let hasBackendErrors = false;

      document.querySelectorAll('.form-control').forEach(input => {
        // ¿Django pintó este campo con is-invalid?
        const isBackendError = input.classList.contains('is-invalid');

        if (isBackendError) {
          // Preservar — marcar el feedback como "propiedad del backend"
          const parent = input.closest('.form-floating') || input.parentElement;
          if (parent) {
            const fb = parent.querySelector('.invalid-feedback');
            if (fb) fb.dataset.backend = '1';  // guarda para no pisar
          }
          hasBackendErrors = true;
        } else {
          // Limpiar is-valid que pudiera venir del HTML sin sentido
          input.classList.remove('is-valid');
        }
      });

      // Focus en primer error del backend
      if (hasBackendErrors) {
        const first = document.querySelector('.form-control.is-invalid');
        setTimeout(() => first?.focus(), 100);
        this.showToast('error', 'Revisa los campos marcados en rojo.');
      } else {
        setTimeout(() => document.getElementById('id_documento')?.focus(), 100);
      }
    }

    /* ── Toasts ──────────────────────────────────────────────── */
    initializeToasts() {
      const configs = {
        success: { delay: 9000,  animation: true },
        error:   { delay: 12000, animation: true },
        warning: { delay: 10000, animation: true },
      };
      Object.entries(configs).forEach(([type, opts]) => {
        const el = document.getElementById(`${type}Toast`);
        if (el) {
          try { this.toasts[type] = new bootstrap.Toast(el, opts); }
          catch (e) { console.error(`[Toast ${type}]`, e); }
        }
      });
    }

    showToast(type, message) {
      const msgEl = document.getElementById(`${type}ToastMessage`);
      const ins   = this.toasts[type];
      if (!msgEl || !ins) return;
      msgEl.textContent = message;
      try { ins.show(); } catch (_) {}
    }

    /* ── Mensajes Django → Toast ─────────────────────────────── */
    convertDjangoMessages() {
      const container = document.getElementById('django-messages');
      if (!container) return;
      container.querySelectorAll('[data-message-level]').forEach(msg => {
        const level = msg.dataset.messageLevel;
        const text  = msg.dataset.messageText;
        if (level.includes('success'))                    this.showToast('success', text);
        else if (level.includes('error') ||
                 level.includes('danger'))                this.showToast('error',   text);
        else                                              this.showToast('warning', text);
      });
    }

    /* ── Toggle contraseña ───────────────────────────────────── */
    initializePasswordToggle() {
      document.querySelectorAll('.toggle-password[data-target]').forEach(btn => {
        if (btn.dataset.initialized) return;  // evitar duplicados
        btn.dataset.initialized = '1';

        const input = document.getElementById(btn.dataset.target);
        if (!input) return;

        btn.addEventListener('click', e => {
          e.preventDefault();
          e.stopPropagation();
          const isText = input.type === 'text';
          input.type   = isText ? 'password' : 'text';
          const icon   = btn.querySelector('i');
          if (icon) icon.className = isText ? 'bi bi-eye' : 'bi bi-eye-slash';
          btn.style.opacity = '0.6';
          setTimeout(() => (btn.style.opacity = '1'), 100);
        });
      });
    }

    /* ── Restricciones de teclado ────────────────────────────── */
    restrictInputs() {
      const doc = document.getElementById('id_documento');
      if (doc) {
        doc.addEventListener('keypress', e => { if (!/[0-9]/.test(e.key)) e.preventDefault(); });
        doc.addEventListener('paste', e => {
          e.preventDefault();
          const nums = (e.clipboardData || window.clipboardData)
            .getData('text').replace(/\D/g, '').slice(0, 10);
          doc.value = nums;
          this.validateField(doc);
        });
      }

      ['id_first_name', 'id_last_name'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('keypress', e => {
          if (!/[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/.test(e.key)) e.preventDefault();
        });
        el.addEventListener('paste', e => {
          e.preventDefault();
          const letters = (e.clipboardData || window.clipboardData)
            .getData('text').replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
          el.value = letters;
          this.validateField(el);
        });
      });
    }

    /* ── Validadores por campo ───────────────────────────────── */
    getValidators() {
      return {
        id_documento: v => {
          const ok = /^\d{10}$/.test(v.trim());
          return { valid: ok, message: ok ? 'Documento válido' : 'Exactamente 10 dígitos numéricos' };
        },
        id_email: v => {
          const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
          return { valid: ok, message: ok ? 'Correo válido' : 'Ingresa un correo válido' };
        },
        id_username: v => {
          const t = v.trim();
          if (t.length < 4)                  return { valid: false, message: 'Mínimo 4 caracteres' };
          if (!/^[a-zA-Z0-9_-]+$/.test(t))  return { valid: false, message: 'Solo letras, números, - y _' };
          return { valid: true, message: 'Usuario válido' };
        },
        id_first_name: v => {
          const ok = v.trim().length > 0 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(v.trim());
          return { valid: ok, message: ok ? 'Nombre válido' : 'Solo puede contener letras' };
        },
        id_last_name: v => {
          const ok = v.trim().length > 0 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(v.trim());
          return { valid: ok, message: ok ? 'Apellido válido' : 'Solo puede contener letras' };
        },
        id_password1: v => {
          const { allValid } = this.checkPasswordRequirements(v);
          return { valid: allValid, message: allValid ? 'Contraseña válida' : 'No cumple todos los requisitos' };
        },
        id_password2: v => {
          const p1  = document.getElementById('id_password1');
          const ok  = !!p1 && v === p1.value && v.length > 0;
          return { valid: ok, message: ok ? 'Las contraseñas coinciden' : 'Las contraseñas no coinciden' };
        },
      };
    }

    /* ── Validar campo individual ────────────────────────────── */
    // FIX BUG 3: siempre retorna boolean
    validateField(input) {
      const validator = this.getValidators()[input.id];
      if (!validator) return true;

      // Campo vacío → limpiar estado, retornar false
      if (input.value.trim().length === 0) {
        input.classList.remove('is-valid', 'is-invalid');
        return false;
      }

      const result = validator(input.value);
      input.classList.remove('is-valid', 'is-invalid');
      input.classList.add(result.valid ? 'is-valid' : 'is-invalid');

      // Actualizar texto del feedback solo si no es del backend
      const parent = input.closest('.form-floating') || input.parentElement;
      if (parent) {
        const inv = parent.querySelector('.invalid-feedback');
        const val = parent.querySelector('.valid-feedback');
        if (!result.valid && inv && !inv.dataset.backend) inv.textContent = result.message;
        if (result.valid  && val && !val.dataset.backend) val.textContent = result.message;
      }

      if (!result.valid) this.shakeElement(input);
      return result.valid;
    }

    /* ── FIX BUG 4: shake con reflow forzado (Safari-safe) ───── */
    shakeElement(element) {
      element.classList.remove('_is-shaking');
      void element.getBoundingClientRect();  // fuerza reflow
      element.classList.add('_is-shaking');
      element.addEventListener('animationend', () => {
        element.classList.remove('_is-shaking');
      }, { once: true });
    }

    /* ── Checklist y barra de contraseña ─────────────────────── */
    checkPasswordRequirements(password) {
      let fulfilled = 0;
      const total   = Object.keys(this.passwordRequirements).length;

      Object.values(this.passwordRequirements).forEach(req => {
        const met  = req.regex.test(password);
        const el   = document.getElementById(req.element);
        if (!el) return;
        const icon = el.querySelector('i');
        if (icon) icon.className = met ? 'bi bi-check-circle-fill text-success' : 'bi bi-circle text-muted';
        el.classList.toggle('text-success', met);
        el.classList.toggle('text-muted',  !met);
        if (met) fulfilled++;
      });

      return { fulfilled, total, allValid: fulfilled === total };
    }

    updatePasswordProgress(password) {
      const bar  = document.getElementById('password-progress');
      const text = document.getElementById('password-strength-text');
      if (!bar) return;

      const { fulfilled, total } = this.checkPasswordRequirements(password);
      const pct = Math.round((fulfilled / total) * 100);

      bar.style.width = pct + '%';
      bar.setAttribute('aria-valuenow', pct);
      bar.className = 'progress-bar';

      const levels = [
        { max: 0,   cls: 'bg-secondary', label: 'Sin contraseña'  },
        { max: 39,  cls: 'bg-danger',    label: 'Muy débil'        },
        { max: 59,  cls: 'bg-warning',   label: 'Débil'            },
        { max: 79,  cls: 'bg-info',      label: 'Aceptable'        },
        { max: 99,  cls: 'bg-primary',   label: 'Buena'            },
        { max: 100, cls: 'bg-success',   label: '¡Excelente!'      },
      ];
      const level = levels.find(l => pct <= l.max) || levels.at(-1);
      bar.classList.add(level.cls);
      if (text) text.textContent = level.label;

      const sr = bar.querySelector('.visually-hidden');
      if (sr) sr.textContent = `${pct}% completado — ${level.label}`;
    }

    /* ── FIX BUG 1: bindFieldEvents SIN bloque extra de password1 ─
       password1 y password2 se manejan dentro del mismo forEach.    */
    bindFieldEvents() {
      this.fieldsToValidate.forEach(id => {
        const el = document.getElementById(id);
        if (!el) { console.warn(`[Registro] Campo no encontrado: ${id}`); return; }

        el.classList.add('form-control');

        // Validar mientras escribe
        el.addEventListener('input', () => {
          this.validateField(el);

          // Lógica especial de contraseña inline (sin listener extra)
          if (id === 'id_password1') {
            this.updatePasswordProgress(el.value);
            const p2 = document.getElementById('id_password2');
            if (p2?.value.length > 0) this.validateField(p2);
          }
        });

        // Validar al perder foco (si tiene contenido)
        el.addEventListener('blur', () => {
          if (el.value.trim().length > 0) this.validateField(el);
        });

        // Micro-animación focus (escala leve)
        el.addEventListener('focus', () => {
          el.style.transition = 'transform 0.2s ease';
          el.style.transform  = 'scale(1.01)';
        });
        el.addEventListener('blur', () => {
          el.style.transform = 'scale(1)';
        });
      });
    }

    /* ── Validación al enviar ────────────────────────────────── */
    bindFormSubmit() {
      const form = document.querySelector('form[method="post"]');
      if (!form) return;

      form.addEventListener('submit', e => {
        let hasErrors    = false;
        let firstInvalid = null;

        this.fieldsToValidate.forEach(id => {
          const input = document.getElementById(id);
          if (!input) return;

          let ok;
          if (!input.value.trim()) {
            // Campo vacío → marcar inválido
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            const parent = input.closest('.form-floating') || input.parentElement;
            const inv    = parent?.querySelector('.invalid-feedback');
            if (inv && !inv.dataset.backend) inv.textContent = 'Este campo es obligatorio';
            ok = false;
          } else {
            ok = this.validateField(input);
          }

          if (!ok) {
            hasErrors = true;
            if (!firstInvalid) firstInvalid = input;
          }
        });

        if (hasErrors) {
          e.preventDefault();
          this.showToast('warning', 'Corrige los campos marcados en rojo antes de continuar.');
          if (firstInvalid) {
            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { firstInvalid.focus(); this.shakeElement(firstInvalid); }, 300);
          }
        }
      });
    }

    /* ── Optimizaciones móviles ──────────────────────────────── */
    applyMobileOptimizations() {
      document.querySelectorAll('input, select, textarea').forEach(el => {
        if (parseFloat(getComputedStyle(el).fontSize) < 16) el.style.fontSize = '16px';
      });
    }
  }

  /* ── Init ────────────────────────────────────────────────────── */
  function init() {
    if (typeof bootstrap === 'undefined') {
      console.error('[Registro] Bootstrap 5 no cargado.');
      return;
    }
    new RegistroValidator().initialize();
  }

  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', init)
    : init();

})();


/* ═══════════════════════════════════════════════════════════════
   SLIDESHOW — módulo independiente
═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  function initSlideshow() {
    const container = document.getElementById('bg-slideshow');
    if (!container) return;
    const slides = [...container.querySelectorAll('.slide')];
    if (!slides.length) return;

    let idx   = 0;
    let timer = null;

    const show = i => slides.forEach((s, n) => s.classList.toggle('active', n === i));
    const next = () => { idx = (idx + 1) % slides.length; show(idx); };

    show(0);
    timer = setInterval(next, 10000);

    container.addEventListener('click', () => {
      clearInterval(timer);
      next();
      timer = setInterval(next, 10000);
    });
  }

  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', initSlideshow)
    : initSlideshow();
})();