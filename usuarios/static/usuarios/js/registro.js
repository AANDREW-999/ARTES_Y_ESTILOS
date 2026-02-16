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

// UX de alerts: scroll al primero y auto-ocultar
(function(){
  const alerts = Array.from(document.querySelectorAll('.alert'));
  if (!alerts.length) return;
  const first = alerts[0];
  first.scrollIntoView({ behavior: 'smooth', block: 'center' });
  alerts.forEach(alert => {
    const tags = alert.getAttribute('data-message-tags') || '';
    const isError = tags.includes('level-error');
    const timeout = isError ? 7000 : 4000;
    setTimeout(() => {
      alert.classList.remove('show');
      alert.remove();
    }, timeout);
  });
})();
