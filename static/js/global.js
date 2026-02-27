// static/js/global.js
(() => {
  'use strict';

  const THEME_KEY = 'site-theme'; // 'light' | 'dark'

  // -------------------------
  // Theme (persistencia + toggle)
  // -------------------------
  const Theme = {
    init() {
      // soporta tanto 'theme-toggle' como 'toggleTheme' para compatibilidad con plantillas existentes
      this.toggleBtn = document.getElementById('theme-toggle') || document.getElementById('toggleTheme');
      const saved = localStorage.getItem(THEME_KEY);
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      const theme = saved || (prefersDark ? 'dark' : 'light');
      this.apply(theme);
      if (this.toggleBtn) this.toggleBtn.addEventListener('click', () => this.toggle());
    },
    apply(theme) {
      document.documentElement.setAttribute('data-bs-theme', theme);
      localStorage.setItem(THEME_KEY, theme);
      if (this.toggleBtn) {
        this.toggleBtn.setAttribute('aria-pressed', theme === 'dark');
        // Opcional: cambiar icono
        this.toggleBtn.classList.toggle('is-dark', theme === 'dark');
      }
    },
    toggle() {
      const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
      this.apply(current === 'dark' ? 'light' : 'dark');
    }
  };

  // -------------------------
  // Bootstrap toasts auto show
  // -------------------------
  function showBootstrapToasts() {
    if (typeof bootstrap === 'undefined') return;
    document.querySelectorAll('.toast[data-autoshow="true"], .toast.show-on-load').forEach(t => {
      try {
        const instance = bootstrap.Toast.getOrCreateInstance(t);
        instance.show();
      } catch (e) {
        // no-op
      }
    });
  }

  // -------------------------
  // Smooth scroll to anchors
  // -------------------------
  function initSmoothScroll() {
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      const href = a.getAttribute('href');
      if (!href || href === '#') return;
      const id = href.slice(1);
      const target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Opcional: update hash without jumping
        history.replaceState(null, '', '#' + id);
      }
    }, { passive: true });
  }

  // -------------------------
  // Navbar scroll style (throttled via rAF)
  // -------------------------
  function initNavbarScroll() {
    const navbar = document.querySelector('.navbar-sticky'); // asegúrate de usar esta clase en tu navbar
    if (!navbar) return;
    let ticking = false;
    const threshold = 50;

    function update() {
      const scrolled = window.scrollY > threshold;
      navbar.classList.toggle('navbar-scrolled', scrolled);
      ticking = false;
    }

    window.addEventListener('scroll', () => {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(update);
      }
    }, { passive: true });

    // init
    update();
  }

  // -------------------------
  // WhatsApp FAB: posicion y comportamiento
  // - Añadir clase .whatsapp-fab al elemento
  // - Añadir footer semántico <footer> para evitar solapamiento
  // -------------------------
  function initWhatsAppFab() {
    const fab = document.querySelector('.whatsapp-fab');
    if (!fab) return;
    const footer = document.querySelector('footer');

    // Hover subtle handled by CSS; here solo controlamos comportamiento cerca del footer
    if (footer && 'IntersectionObserver' in window) {
      const obs = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            fab.classList.add('fab-near-footer');
          } else {
            fab.classList.remove('fab-near-footer');
          }
        });
      }, { root: null, threshold: 0 });

      obs.observe(footer);
    }

    // Evitar múltiples listeners — solo uno por FAB
    if (!fab.dataset.listenerAttached) {
      fab.addEventListener('mouseenter', () => fab.classList.add('fab-hover'));
      fab.addEventListener('mouseleave', () => fab.classList.remove('fab-hover'));
      fab.dataset.listenerAttached = 'true';
    }
  }

  // -------------------------
  // Inicialización
  // -------------------------
  function init() {
    Theme.init();
    showBootstrapToasts();
    initSmoothScroll();
    initNavbarScroll();
    initWhatsAppFab();
  }

  // Esperar DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export pequeño (opcional para debugging)
  window.siteGlobal = {
    toggleTheme: () => Theme.toggle(),
    currentTheme: () => document.documentElement.getAttribute('data-bs-theme')
  };
})();