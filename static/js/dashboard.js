/**
 * DASHBOARD.JS - Panel Administrativo Profesional
 * Sistema de navegación, toasts y funcionalidades del panel
 * @version 2.0
 * @date 2026-02-20
 */

(function() {
    'use strict';

    class DashboardManager {
        constructor() {
            this.sidebar = null;
            this.sidebarToggle = null;
            this.toasts = {};
            this.init();
        }

        init() {
            console.log('🌸 Iniciando Panel Administrativo...');

            this.initElements();
            this.initSidebarToggle();
            this.initToasts();
            this.initActiveMenuDetection();
            this.initSubMenus();
            this.convertDjangoMessages();
            this.initResponsive();

            console.log('✅ Panel Administrativo iniciado');
        }

        // ============================================
        // INICIALIZACIÓN DE ELEMENTOS
        // ============================================
        initElements() {
            this.sidebar = document.getElementById('sidebar');
            this.sidebarToggle = document.getElementById('sidebar-toggle');

            // Toasts
            this.toasts.success = document.getElementById('successToast');
            this.toasts.error = document.getElementById('errorToast');
            this.toasts.warning = document.getElementById('warningToast');

            if (typeof bootstrap !== 'undefined') {
                if (this.toasts.success) this.toasts.success = new bootstrap.Toast(this.toasts.success);
                if (this.toasts.error) this.toasts.error = new bootstrap.Toast(this.toasts.error);
                if (this.toasts.warning) this.toasts.warning = new bootstrap.Toast(this.toasts.warning);
            }
        }

        // ============================================
        // TOGGLE DEL SIDEBAR
        // ============================================
        initSidebarToggle() {
            if (this.sidebarToggle && this.sidebar) {
                this.sidebarToggle.addEventListener('click', () => {
                    this.sidebar.classList.toggle('show');
                });

                // Cerrar sidebar al hacer click fuera (móvil)
                document.addEventListener('click', (e) => {
                    if (window.innerWidth <= 768) {
                        if (!this.sidebar.contains(e.target) &&
                            !this.sidebarToggle.contains(e.target) &&
                            this.sidebar.classList.contains('show')) {
                            this.sidebar.classList.remove('show');
                        }
                    }
                });
            }
        }

        // ============================================
        // SISTEMA DE TOASTS
        // ============================================
        initToasts() {
            console.log('📢 Sistema de toasts inicializado');
        }

        showToast(type, message) {
            const messageElement = document.getElementById(`${type}ToastMessage`);
            if (messageElement && this.toasts[type]) {
                messageElement.textContent = message;
                this.toasts[type].show();
            }
        }

        convertDjangoMessages() {
            const messagesContainer = document.getElementById('django-messages');
            if (!messagesContainer) return;

            const messages = messagesContainer.querySelectorAll('[data-message-level]');
            messages.forEach(msg => {
                const level = msg.getAttribute('data-message-level');
                const text = msg.getAttribute('data-message-text');

                let type = 'success';
                if (level.includes('error') || level.includes('danger')) {
                    type = 'error';
                } else if (level.includes('warning')) {
                    type = 'warning';
                }

                setTimeout(() => this.showToast(type, text), 300);
            });
        }

        // ============================================
        // DETECCIÓN DE MENÚ ACTIVO
        // ============================================
        initActiveMenuDetection() {
            const currentPath = window.location.pathname;
            const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');

            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href && href !== '#' && currentPath.includes(href)) {
                    link.classList.add('active');

                    // Si está en un submenú, abrirlo
                    const collapse = link.closest('.collapse');
                    if (collapse) {
                        collapse.classList.add('show');
                        const parentLink = document.querySelector(`[href="#${collapse.id}"]`);
                        if (parentLink) {
                            parentLink.classList.remove('collapsed');
                            parentLink.setAttribute('aria-expanded', 'true');
                        }
                    }
                }
            });
        }

        // ============================================
        // SUBMENÚS MEJORADOS
        // ============================================
        initSubMenus() {
            const subMenuToggles = document.querySelectorAll('[data-bs-toggle="collapse"]');

            subMenuToggles.forEach(toggle => {
                const targetId = toggle.getAttribute('href');
                const target = document.querySelector(targetId);

                if (!target) return;

                // Añadir clases para animación
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();

                    const isExpanded = toggle.getAttribute('aria-expanded') === 'true';

                    // Cerrar otros submenús (opcional)
                    // this.closeOtherSubmenus(targetId);

                    if (isExpanded) {
                        target.classList.remove('show');
                        toggle.classList.add('collapsed');
                        toggle.setAttribute('aria-expanded', 'false');
                    } else {
                        target.classList.add('show');
                        toggle.classList.remove('collapsed');
                        toggle.setAttribute('aria-expanded', 'true');
                    }
                });

                // Efecto hover en items de submenú
                const subItems = target.querySelectorAll('.nav-link');
                subItems.forEach(item => {
                    item.addEventListener('mouseenter', () => {
                        item.style.transform = 'translateX(4px)';
                    });

                    item.addEventListener('mouseleave', () => {
                        item.style.transform = 'translateX(0)';
                    });
                });
            });
        }

        closeOtherSubmenus(exceptId) {
            const allCollapses = document.querySelectorAll('.sidebar .collapse');
            allCollapses.forEach(collapse => {
                if (`#${collapse.id}` !== exceptId && collapse.classList.contains('show')) {
                    collapse.classList.remove('show');
                    const parentLink = document.querySelector(`[href="#${collapse.id}"]`);
                    if (parentLink) {
                        parentLink.classList.add('collapsed');
                        parentLink.setAttribute('aria-expanded', 'false');
                    }
                }
            });
        }

        // ============================================
        // RESPONSIVE
        // ============================================
        initResponsive() {
            window.addEventListener('resize', () => {
                if (window.innerWidth > 768 && this.sidebar) {
                    this.sidebar.classList.remove('show');
                }
            });
        }
    }

    // ============================================
    // INICIALIZACIÓN AUTOMÁTICA
    // ============================================
    function init() {
        new DashboardManager();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

