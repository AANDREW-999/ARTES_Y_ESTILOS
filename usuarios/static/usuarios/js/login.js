// Toggle de mostrar/ocultar contraseña en el login
(function(){
  const toggleBtn = document.querySelector('.toggle-password');
  const inputPwd = document.getElementById('id_password');
  if (!toggleBtn || !inputPwd) return;
  toggleBtn.addEventListener('click', () => {
    const isText = inputPwd.getAttribute('type') === 'text';
    inputPwd.setAttribute('type', isText ? 'password' : 'text');
    toggleBtn.innerHTML = isText ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
  });
})();

// Ajuste rápido: asegurar que los inputs form-floating tengan clases correctas si el form no las trae
(function(){
  const inputUsername = document.getElementById('id_username');
  const inputPassword = document.getElementById('id_password');
  [inputUsername, inputPassword].forEach(el => {
    if (el && !el.classList.contains('form-control')) {
      el.classList.add('form-control');
    }
    // Placeholders para mejor UX
    if (el === inputUsername && !el.placeholder) el.placeholder = 'Ingrese su documento';
    if (el === inputPassword && !el.placeholder) el.placeholder = 'Ingrese su contraseña';
  });
})();

// Slideshow de fondo: cambio cada 5 segundos (5000 ms)
(function(){
  const container = document.getElementById('bg-slideshow');
  if (!container) return;
  const slides = Array.from(container.querySelectorAll('.slide'));
  if (slides.length === 0) return;

  let idx = 0;
  const activate = (i) => {
    slides.forEach((s, k) => s.classList.toggle('active', k === i));
  };
  activate(idx);

  setInterval(() => {
    idx = (idx + 1) % slides.length;
    activate(idx);
  }, 15000); // 10 segundos
})();
