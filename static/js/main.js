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

  // Evitar dobles instancias (data-bs-ride + init JS) y dejar el avance 1 a 1.
  const carousel = bootstrap.Carousel.getOrCreateInstance(carouselEl, {
    interval: 4500,     // más calmado
    ride: false,        // inicio manual, lo activamos programáticamente
    pause: 'hover',
    wrap: true
  });

  carouselEl.classList.add('carousel-fade');
  carousel.cycle();

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

  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeLightbox(); });
  btnClose && btnClose.addEventListener('click', closeLightbox);
  window.addEventListener('resize', () => { if (overlay.classList.contains('show')) fitImageNatural(imgEl); });
})();
