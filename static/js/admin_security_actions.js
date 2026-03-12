/**
 * ADMIN_SECURITY_ACTIONS.JS
 * Confirmaciones y acciones sensibles con overlay del panel.
 * - Evita confirm() nativo del navegador.
 * - Permite descargas (backup) via fetch/blob para mostrar notificación.
 */

(function () {
  'use strict';

  function getDashboard() {
    return window._dashboard || null;
  }

  function showNotification(type, message) {
    const dashboard = getDashboard();
    if (dashboard && typeof dashboard.showAdminNotification === 'function') {
      dashboard.showAdminNotification(type, message);
      return;
    }

    // Fallback mínimo si no existe overlay
    if (type === 'error') alert(message);
    else console.log(message);
  }

  function showConfirm(type, message, onConfirm, onCancel) {
    const dashboard = getDashboard();
    if (dashboard && typeof dashboard.showAdminConfirm === 'function') {
      dashboard.showAdminConfirm(type, message, onConfirm, onCancel);
      return;
    }

    // Fallback (último recurso)
    if (window.confirm(message)) onConfirm && onConfirm();
    else onCancel && onCancel();
  }

  function getCsrfTokenFromForm(form) {
    const input = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : '';
  }

  function parseFilenameFromContentDisposition(headerValue) {
    if (!headerValue) return '';

    // filename*=UTF-8''...
    const matchStar = headerValue.match(/filename\*=(?:UTF-8'')?([^;]+)/i);
    if (matchStar && matchStar[1]) {
      return decodeURIComponent(matchStar[1].trim().replace(/^"|"$/g, ''));
    }

    const match = headerValue.match(/filename=([^;]+)/i);
    if (match && match[1]) {
      return match[1].trim().replace(/^"|"$/g, '');
    }

    return '';
  }

  function parseAllowedExtensions(value) {
    if (!value) return [];
    return value
      .split(',')
      .map((s) => (s || '').trim().toLowerCase())
      .filter((s) => s.length > 0)
      .map((s) => (s.startsWith('.') ? s : `.${s}`));
  }

  function getFileInputForForm(form) {
    // Primera opción: input[type=file] dentro del form
    return form.querySelector('input[type="file"]');
  }

  function getSubmitButtonForForm(form) {
    return form.querySelector('button[type="submit"], input[type="submit"]');
  }

  function isFileExtensionAllowed(filename, allowedExts) {
    if (!allowedExts || allowedExts.length === 0) return true;
    const lower = (filename || '').toLowerCase();
    return allowedExts.some((ext) => lower.endsWith(ext));
  }

  function validateRequiredFileSelection(form, notifyOnError) {
    const fileInput = getFileInputForForm(form);
    if (!fileInput) {
      if (notifyOnError) {
        showNotification('error', 'No se encontró el campo de archivo para esta acción.');
      }
      return false;
    }

    const files = fileInput.files;
    const hasFile = !!(files && files.length > 0);
    if (!hasFile) {
      if (notifyOnError) {
        showNotification('error', 'Debes seleccionar un archivo válido antes de restaurar.');
      }
      return false;
    }

    const allowedAttr = form.getAttribute('data-admin-allowed-ext') || fileInput.getAttribute('accept') || '';
    const allowedExts = parseAllowedExtensions(allowedAttr);
    const filename = files[0]?.name || '';

    if (!isFileExtensionAllowed(filename, allowedExts)) {
      fileInput.value = '';
      if (notifyOnError) {
        showNotification('error', 'Formato de archivo no permitido. Selecciona un archivo SQLite válido (.sqlite3, .sqlite, .db).');
      }
      return false;
    }

    return true;
  }

  function updateRequireFileState(form) {
    const fileInput = getFileInputForForm(form);
    const submitBtn = getSubmitButtonForForm(form);
    if (!fileInput || !submitBtn) return;

    const isValid = validateRequiredFileSelection(form, false);
    submitBtn.disabled = !isValid;
  }

  function bindRequireFileForms() {
    const forms = Array.from(document.querySelectorAll('form[data-admin-require-file]'));
    forms.forEach((form) => {
      if (form.dataset.adminRequireFileBound === '1') return;
      form.dataset.adminRequireFileBound = '1';

      const fileInput = getFileInputForForm(form);
      if (fileInput) {
        fileInput.addEventListener('change', () => updateRequireFileState(form));
        fileInput.addEventListener('input', () => updateRequireFileState(form));
      }

      // Estado inicial
      updateRequireFileState(form);
    });

    // Listener delegado como respaldo (por compatibilidad de algunos navegadores/componentes)
    if (document.body && document.body.dataset.adminRequireFileDelegatedBound !== '1') {
      document.body.dataset.adminRequireFileDelegatedBound = '1';
      document.body.addEventListener('change', (event) => {
        const target = event.target;
        if (!(target instanceof HTMLInputElement) || target.type !== 'file') return;
        const form = target.closest('form[data-admin-require-file]');
        if (!form) return;
        updateRequireFileState(form);
      });
    }
  }

  async function downloadViaFetch(form) {
    const action = form.getAttribute('action');
    const csrfToken = getCsrfTokenFromForm(form);

    const response = await fetch(action, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'same-origin'
    });

    if (!response.ok) {
      // Intentar leer error JSON
      let message = 'No fue posible completar la operación.';
      try {
        const data = await response.json();
        if (data && data.message) message = data.message;
      } catch (_) {
        // Podría venir HTML de redirect
        try {
          const text = await response.text();
          if (text) message = 'No fue posible generar el backup. Revisa permisos o configuración.';
        } catch (_) {}
      }
      throw new Error(message);
    }

    const blob = await response.blob();
    const cd = response.headers.get('content-disposition') || '';
    const filename = parseFilenameFromContentDisposition(cd) || 'backup.sqlite3';

    const url = window.URL.createObjectURL(blob);
    try {
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } finally {
      window.URL.revokeObjectURL(url);
    }

    return filename;
  }

  function bindConfirmForms() {
    const forms = Array.from(document.querySelectorAll('form[data-admin-confirm]'));
    forms.forEach((form) => {
      if (form.dataset.adminConfirmBound === '1') return;
      form.dataset.adminConfirmBound = '1';

      form.addEventListener('submit', (e) => {
        e.preventDefault();

        // Si el form requiere archivo, validar antes de confirmar
        if (form.hasAttribute('data-admin-require-file')) {
          updateRequireFileState(form);

          const canSubmit = validateRequiredFileSelection(form, true);
          if (!canSubmit) {
            return;
          }
        }

        const type = (form.getAttribute('data-admin-confirm-type') || 'warning').toLowerCase();
        const message = form.getAttribute('data-admin-confirm-message') || '¿Deseas continuar con esta acción?';

        // Evitar doble submit
        if (form.dataset.adminConfirmSubmitting === '1') return;

        showConfirm(type, message, () => {
          // Caso especial: descarga AJAX
          if (form.hasAttribute('data-admin-ajax-download')) {
            if (form.dataset.adminConfirmSubmitting === '1') return;
            form.dataset.adminConfirmSubmitting = '1';

            showNotification('info', form.getAttribute('data-admin-progress-message') || 'Procesando...');

            downloadViaFetch(form)
              .then((filename) => {
                showNotification('success', `Copia de seguridad generada correctamente. Descarga iniciada: ${filename}.`);
              })
              .catch((err) => {
                showNotification('error', err?.message || 'No fue posible generar el backup.');
              })
              .finally(() => {
                form.dataset.adminConfirmSubmitting = '0';
              });
            return;
          }

          // Submit normal (restauración multipart, etc.)
          form.dataset.adminConfirmSubmitting = '1';

          const progress = form.getAttribute('data-admin-progress-message');
          if (progress) showNotification('info', progress);

          form.submit();
        }, () => {
          // cancel
        });
      });
    });
  }

  function init() {
    bindRequireFileForms();
    bindConfirmForms();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
