// Carrusel de fondo para Registro (5s)
(function(){
  const container = document.getElementById('bg-slideshow');
  if (!container) return;
  const slides = Array.from(container.querySelectorAll('.slide'));
  if (slides.length === 0) return;
  let idx = 0;
  const activate = (i) => slides.forEach((s,k)=>s.classList.toggle('active',k===i));
  activate(idx);
  setInterval(()=>{idx=(idx+1)%slides.length;activate(idx);},5000);
})();

// Ojito para password1 y password2
(function(){
  document.querySelectorAll('.toggle-password').forEach(btn=>{
    const targetId = btn.getAttribute('data-target');
    const inputPwd = document.getElementById(targetId);
    if (!inputPwd) return;
    btn.addEventListener('click',()=>{
      const isText = inputPwd.type === 'text';
      inputPwd.type = isText ? 'password' : 'text';
      btn.innerHTML = isText ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
    });
  });
})();
