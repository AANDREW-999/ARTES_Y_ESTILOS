// JavaScript global del proyecto
const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-link");

window.addEventListener("scroll", () => {
    let current = "";

    sections.forEach(section => {
        const sectionTop = section.offsetTop - 120;
        if (scrollY >= sectionTop) {
            current = section.getAttribute("id");
        }
    });

    navLinks.forEach(link => {
        link.classList.remove("active");
        if (link.getAttribute("href") === "#" + current) {
            link.classList.add("active");
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('Proyecto Django cargado correctamente');
    
    // Cerrar alertas automáticamente después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });

  // Animación de brand con rebote suave
  const brand = document.querySelector('.brand-animated');
  if (brand) {
    brand.addEventListener('mouseenter', () => {
      brand.style.transition = 'transform .25s ease';
      brand.style.transform = 'translateY(-2px) scale(1.05)';
    });
    brand.addEventListener('mouseleave', () => {
      brand.style.transform = 'translateY(0) scale(1)';
    });
  }
});

(function(){
  const carouselEl = document.getElementById('carouselAye');
  if (!carouselEl || !window.bootstrap) return;

  const carousel = new bootstrap.Carousel(carouselEl, {
    interval: 3500,     // 3.5s entre slides
    ride: false,        // inicio manual, lo activamos programáticamente
    pause: 'hover',     // pausa al pasar el mouse
    wrap: true          // ciclo infinito
  });
  // Iniciar autoplay
  carousel.cycle();
  carouselEl.classList.add('carousel-fade'); // transición crossfade más suave

  // Avance/retroceso continuo mientras se mantiene el botón presionado
  const prevBtn = carouselEl.querySelector('.carousel-control-prev');
  const nextBtn = carouselEl.querySelector('.carousel-control-next');

  let holdInterval = null;

  function markReveal(direction){
    const items = carouselEl.querySelectorAll('.carousel-item');
    const active = carouselEl.querySelector('.carousel-item.active');
    if (!active) return;
    let target;
    if (direction === 'next') {
      target = active.nextElementSibling || items[0];
      target && target.classList.add('next-reveal');
    } else {
      target = active.previousElementSibling || items[items.length - 1];
      target && target.classList.add('prev-reveal');
    }
    // limpiar marcas tras la transición
    setTimeout(() => {
      items.forEach(i => i.classList.remove('next-reveal', 'prev-reveal'));
    }, 900);
  }

  function startHold(direction){
    carouselEl.classList.add('hold-advance');
    markReveal(direction);
    direction === 'next' ? carousel.next() : carousel.prev();
    holdInterval = setInterval(() => {
      markReveal(direction);
      direction === 'next' ? carousel.next() : carousel.prev();
    }, 900);
  }
  function stopHold(){
    carouselEl.classList.remove('hold-advance');
    clearInterval(holdInterval);
    holdInterval = null;
  }

  if (nextBtn){
    nextBtn.addEventListener('mousedown', () => startHold('next'));
    nextBtn.addEventListener('mouseup', stopHold);
    nextBtn.addEventListener('mouseleave', stopHold);
    nextBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startHold('next'); });
    nextBtn.addEventListener('touchend', stopHold);
    nextBtn.addEventListener('touchcancel', stopHold);
  }
  if (prevBtn){
    prevBtn.addEventListener('mousedown', () => startHold('prev'));
    prevBtn.addEventListener('mouseup', stopHold);
    prevBtn.addEventListener('mouseleave', stopHold);
    prevBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startHold('prev'); });
    prevBtn.addEventListener('touchend', stopHold);
    prevBtn.addEventListener('touchcancel', stopHold);
  }

  // Mejorar accesibilidad: pausar con enfoque del carrusel mediante teclado
  carouselEl.addEventListener('focusin', () => carousel.pause());
  carouselEl.addEventListener('focusout', () => carousel.cycle());
})();

(function(){
  // IntersectionObserver para revelar elementos con clases .reveal, .reveal-left, .reveal-right
  const els = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  if (!('IntersectionObserver' in window) || els.length === 0) return;
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('in-view');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });
  els.forEach(el => obs.observe(el));
})();

(function(){
  const overlay = document.getElementById('lightboxOverlay');
  const imgEl = document.getElementById('lightboxImage');
  const btnClose = document.getElementById('lightboxClose');
  if (!overlay || !imgEl) return;

  function fitImageNatural(image){
    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    const vh = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
    const maxW = vw * 0.9;
    const maxH = vh * 0.85;
    const natW = image.naturalWidth;
    const natH = image.naturalHeight;
    // Escala proporcional sin superar límites
    const scale = Math.min(maxW / natW, maxH / natH, 1); // nunca escalar por encima del tamaño natural
    const targetW = Math.floor(natW * scale);
    const targetH = Math.floor(natH * scale);
    imgEl.style.width = targetW + 'px';
    imgEl.style.height = targetH + 'px';
  }

  function openLightbox(src){
    imgEl.onload = () => fitImageNatural(imgEl);
    imgEl.src = src;
    overlay.classList.add('show');
    overlay.setAttribute('aria-hidden','false');
  }
  function closeLightbox(){
    overlay.classList.remove('show');
    overlay.setAttribute('aria-hidden','true');
    imgEl.src = '#';
    imgEl.style.width = '';
    imgEl.style.height = '';
  }

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const section = document.querySelector(this.getAttribute('href'));
        section.scrollIntoView({
            behavior: 'smooth'
        });
    });
});
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeLightbox(); });
  btnClose && btnClose.addEventListener('click', closeLightbox);
  window.addEventListener('resize', () => { if (overlay.classList.contains('show')) fitImageNatural(imgEl); });
})();
