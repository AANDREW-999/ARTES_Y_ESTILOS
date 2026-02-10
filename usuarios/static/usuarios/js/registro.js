// Toggle de mostrar/ocultar contraseña en registro (múltiples campos con data-target)
(function(){
  const buttons = document.querySelectorAll('.toggle-password[data-target]');
  if (!buttons.length) return;
  buttons.forEach(btn => {
    const targetId = btn.getAttribute('data-target');
    const input = document.getElementById(targetId);
    if (!input) return;
    btn.addEventListener('click', () => {
      const isText = input.getAttribute('type') === 'text';
      input.setAttribute('type', isText ? 'password' : 'text');
      btn.innerHTML = isText ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
    });
  });
})();

// Normalización de clases y placeholders para inputs del registro
(function(){
  const ids = ['id_documento','id_email','id_first_name','id_last_name','id_password1','id_password2','id_telefono'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    if (!el.classList.contains('form-control')) el.classList.add('form-control');
    if (!el.placeholder) {
      switch(id){
        case 'id_documento': el.placeholder = 'Documento'; break;
        case 'id_email': el.placeholder = 'Correo electrónico'; break;
        case 'id_first_name': el.placeholder = 'Nombre'; break;
        case 'id_last_name': el.placeholder = 'Apellido'; break;
        case 'id_password1': el.placeholder = 'Password'; break;
        case 'id_password2': el.placeholder = 'Confirmar password'; break;
        case 'id_telefono': el.placeholder = 'Teléfono (opcional)'; break;
      }
    }
  });
})();

// Slideshow de fondo (compartido con login)
(function(){
  const container = document.getElementById('bg-slideshow');
  if (!container) return;
  const slides = Array.from(container.querySelectorAll('.slide'));
  if (!slides.length) return;
  let idx = 0;
  const activate = i => slides.forEach((s, k) => s.classList.toggle('active', k === i));
  activate(idx);
  setInterval(() => { idx = (idx + 1) % slides.length; activate(idx); }, 10000);
})();

// Envío del formulario de registro con feedback y redirección al login
(function(){
  const form = document.querySelector('form[method="post"]');
  if (!form) return;

  const showAlert = (type, message, autoHideMs = 4000) => {
    const existing = form.querySelector('.alert');
    if (existing) existing.remove();
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
      <div class="d-flex align-items-center">
        <i class="bi ${type === 'success' ? 'bi-check-circle' : type === 'warning' ? 'bi-exclamation-triangle' : 'bi-x-circle'} me-2"></i>
        <span>${message}</span>
      </div>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
    `;
    form.prepend(alert);
    if (autoHideMs) {
      setTimeout(() => { alert.classList.remove('show'); alert.remove(); }, autoHideMs);
    }
  };

  const submitBtn = form.querySelector('.btn-registrarme') || form.querySelector('button[type="submit"]');
  const originalBtnHtml = submitBtn ? submitBtn.innerHTML : '';

  const setSubmitting = (on) => {
    if (!submitBtn) return;
    submitBtn.disabled = on;
    submitBtn.innerHTML = on ? '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Procesando…' : originalBtnHtml;
  };

  const clearErrors = () => {
    form.querySelectorAll('.text-danger.small').forEach(e => e.remove());
  };

  const renderErrors = async (resp) => {
    let data;
    try { data = await resp.json(); } catch {
      showAlert('danger', 'El servidor no devolvió detalles de error.');
      return;
    }
    if (!data || typeof data !== 'object') return;
    if (data.detail || data.message) {
      showAlert('warning', data.detail || data.message);
    }
    Object.entries(data).forEach(([field, msgs]) => {
      const input = document.getElementById(`id_${field}`);
      const container = input ? (input.closest('.form-floating') || input.parentElement) : null;
      const msg = Array.isArray(msgs) ? msgs[0] : String(msgs);
      if (container && msg) {
        const div = document.createElement('div');
        div.className = 'text-danger small';
        div.textContent = msg;
        container.appendChild(div);
      }
    });
  };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors();
    setSubmitting(true);
    try {
      const action = form.getAttribute('action') || window.location.href;
      const fd = new FormData(form);
      const resp = await fetch(action, {
        method: 'POST',
        body: fd,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      if (resp.redirected) {
        showAlert('success', 'Usuario registrado correctamente. Redirigiendo al inicio de sesión…', 2500);
        setTimeout(() => { window.location.href = resp.url; }, 1800);
        return;
      }

      if (resp.ok) {
        let data = null;
        try { data = await resp.json(); } catch {}
        showAlert('success', (data && data.message) ? data.message : 'Usuario registrado correctamente. Redirigiendo al inicio de sesión…', 2500);
        setTimeout(() => {
          if (data && data.redirect_to) {
            window.location.href = data.redirect_to;
          } else {
            window.location.href = (document.querySelector('a[href*="/login/"]') || { href: '/' }).href;
          }
        }, 1800);
      } else {
        await renderErrors(resp);
      }
    } catch (err) {
      showAlert('danger', 'Ocurrió un error al registrar. Inténtalo de nuevo.');
    } finally {
      setSubmitting(false);
    }
  });
})();
