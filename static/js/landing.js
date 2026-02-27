// static/js/landing.js
(() => {
  'use strict';

  // IntersectionObserver para "reveal" animations
  function initReveal() {
    const selector = '[data-reveal], .reveal, .reveal-left, .reveal-right';
    const elements = Array.from(document.querySelectorAll(selector));

    if (elements.length === 0) return;

    if (!('IntersectionObserver' in window)) {
      // Fallback: mostrar todo inmediatamente
      elements.forEach(el => el.classList.add('revealed'));
      return;
    }

    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Añadimos clases compatibles: 'revealed' y 'in-view'
          entry.target.classList.add('revealed', 'in-view');
          // si el elemento no quiere ser observado solo una vez, puede tener data-reveal-once="false"
          if (entry.target.dataset.revealOnce !== 'false') obs.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.12
    });

    elements.forEach(el => observer.observe(el));
  }

  // Contadores simples (opcional)
  function initCounters() {
    document.querySelectorAll('[data-counter]').forEach(el => {
      const to = parseInt(el.dataset.counter, 10) || 0;
      const duration = parseInt(el.dataset-duration, 10) || 1200;
      let start = 0;
      const startTime = performance.now();
      function tick(now) {
        const progress = Math.min((now - startTime) / duration, 1);
        el.textContent = Math.floor(progress * to);
        if (progress < 1) requestAnimationFrame(tick);
        else el.textContent = to;
      }
      requestAnimationFrame(tick);
    });
  }

  // Inicializar solo si estamos en landing: detectar sección hero
  function initLandingSpecific() {
    const hero = document.getElementById('hero');
    if (!hero) return;
    // ejemplo: animar CTA
    // Intentar selector marcado, si no existe tomar el primer botón principal
    let cta = hero.querySelector('[data-hero-cta]');
    if (!cta) cta = hero.querySelector('.btn-rosa, .btn-primary, .btn');
    if (cta) setTimeout(() => cta.classList.add('revealed', 'in-view'), 300);
  }

  function init() {
    initReveal();
    initCounters();
    initLandingSpecific();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();