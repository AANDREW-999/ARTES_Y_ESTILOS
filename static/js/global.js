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
    const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function flashScrollTarget(target) {
      if (!target) return;

      // Preferimos resaltar el contenedor para que se vea más “pro” (no un overlay de pantalla completa)
      const focusEl = target.querySelector?.('.container, .section-card, .card') || target;
      const cls = 'scroll-focus';

      focusEl.classList.remove(cls);
      // Forzar reflow para reiniciar animación si se hace click rápido
      void focusEl.offsetHeight;
      focusEl.classList.add(cls);

      window.setTimeout(() => focusEl.classList.remove(cls), prefersReduced ? 250 : 950);
    }

    function getAnchorTargetFromHref(href) {
      if (!href || href === '#') return null;
      const id = href.slice(1);
      if (!id) return null;
      return document.getElementById(id);
    }

    function getScrollYForTarget(target) {
      const navbar = document.getElementById('mainNavbar');
      const navHeight = navbar ? navbar.offsetHeight : 0;
      const targetTop = target.getBoundingClientRect().top + window.scrollY;
      const offset = navHeight + 12;
      return Math.max(targetTop - offset, 0);
    }

    function smoothScrollTo(targetY, onDone) {
      if (prefersReduced) {
        window.scrollTo(0, targetY);
        if (typeof onDone === 'function') onDone();
        return;
      }

      const startY = window.scrollY;
      const distance = targetY - startY;
      const maxDuration = 900;
      const minDuration = 350;
      const duration = Math.min(maxDuration, Math.max(minDuration, Math.abs(distance) * 0.5));
      const startTime = performance.now();

      function easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      }

      function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = easeInOutCubic(progress);
        window.scrollTo(0, startY + distance * eased);
        if (progress < 1) requestAnimationFrame(step);
        else if (typeof onDone === 'function') onDone();
      }

      requestAnimationFrame(step);
    }

    // Si se entra a una URL con hash (#sobre, #catalogo, etc), aplicar el mismo offset del navbar
    function handleInitialHash() {
      const hash = window.location.hash;
      if (!hash || hash.length < 2) return;
      const target = getAnchorTargetFromHref(hash);
      if (!target) return;

      // Esperar un frame por si el layout todavía está ajustando alturas
      window.requestAnimationFrame(() => {
        const finalY = getScrollYForTarget(target);
        // En carga inicial preferimos no animar exagerado
        smoothScrollTo(finalY, () => flashScrollTarget(target));
      });
    }

    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      const href = a.getAttribute('href');
      if (!href || href === '#') return;

      const target = getAnchorTargetFromHref(href);
      if (!target) return;

      e.preventDefault();

      // Cerrar el menú móvil si está abierto
      const collapseEl = document.getElementById('navbarNav');
      if (collapseEl && collapseEl.classList.contains('show') && typeof bootstrap !== 'undefined') {
        try {
          const collapse = bootstrap.Collapse.getOrCreateInstance(collapseEl);
          collapse.hide();
        } catch (err) {
          // no-op
        }
      }

      const finalY = getScrollYForTarget(target);
      const id = href.slice(1);

      smoothScrollTo(finalY, () => flashScrollTarget(target));
      history.replaceState(null, '', '#' + id);
    }, { passive: false });

    handleInitialHash();
  }

  // -------------------------
  // Navbar scroll style (throttled via rAF)
  // -------------------------
  function initNavbarScroll() {
    const navbar = document.getElementById('mainNavbar');
    if (!navbar) return;

    let ticking = false;
    let lastY = window.scrollY;
    const threshold = 80;
    const hideOffset = 220;
    let allowHide = window.matchMedia ? window.matchMedia('(min-width: 992px)').matches : true;

    function updateAllowHide() {
      allowHide = window.matchMedia ? window.matchMedia('(min-width: 992px)').matches : true;
      if (!allowHide) {
        navbar.classList.remove('navbar-hidden');
        navbar.classList.add('navbar-visible');
      }
    }

    function update() {
      const currentY = window.scrollY;
      const scrolled = currentY > threshold;
      const goingDown = currentY > lastY;
      const hasFocus = navbar.contains(document.activeElement);
      const menuOpen = !!navbar.querySelector('.navbar-collapse.show');

      navbar.classList.toggle('navbar-scrolled', scrolled);

      // En pantallas pequeñas, no ocultar: siempre visible
      if (!allowHide) {
        navbar.classList.remove('navbar-hidden');
        navbar.classList.add('navbar-visible');
      } else if (!menuOpen && !hasFocus && currentY > hideOffset && goingDown && (currentY - lastY) > 6) {
        navbar.classList.add('navbar-hidden');
        navbar.classList.remove('navbar-visible');
      } else {
        navbar.classList.remove('navbar-hidden');
        navbar.classList.add('navbar-visible');
      }

      lastY = currentY;
      ticking = false;
    }

    window.addEventListener('scroll', () => {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(update);
      }
    }, { passive: true });

    // Recalcular si cambia el tamaño (p.ej. rotación / resize)
    window.addEventListener('resize', updateAllowHide, { passive: true });

    // Si el usuario sube con la rueda, mostrar el navbar de inmediato
    // (mejora accesibilidad/percepción, incluso antes del próximo "scroll" paint)
    let wheelTicking = false;
    window.addEventListener('wheel', (e) => {
      if (wheelTicking) return;
      wheelTicking = true;
      window.requestAnimationFrame(() => {
        wheelTicking = false;
        if (e.deltaY < 0) {
          navbar.classList.remove('navbar-hidden');
          navbar.classList.add('navbar-visible');
        }
      });
    }, { passive: true });

    // Mobile/touch: si el usuario arrastra hacia abajo (scroll up), mostrar navbar
    let lastTouchY = 0;
    window.addEventListener('touchstart', (e) => {
      lastTouchY = e.touches && e.touches.length ? e.touches[0].clientY : 0;
    }, { passive: true });
    window.addEventListener('touchmove', (e) => {
      const y = e.touches && e.touches.length ? e.touches[0].clientY : lastTouchY;
      const goingUp = y > lastTouchY + 6;
      if (goingUp) {
        navbar.classList.remove('navbar-hidden');
        navbar.classList.add('navbar-visible');
      }
      lastTouchY = y;
    }, { passive: true });

    updateAllowHide();
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