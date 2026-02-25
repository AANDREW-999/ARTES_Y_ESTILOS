/**
 * DASHBOARD.JS - Panel Administrativo Profesional
 * Sidebar · Submenús · Notificaciones PRO · Modal Logout
 * @version 6.0
 */

(function () {
    'use strict';

    class DashboardManager {

        constructor() {
            this.sidebar         = null;
            this.sidebarToggle   = null;
            this.adminOverlay    = null;
            this.adminCard       = null;
            this.logoutModal     = null;
            this._autoCloseTimer = null;
            this._escHandler     = null;
            this._outsideHandler = null;
            this.init();
        }

        // ─────────────────────────────────────────
        // INICIALIZACIÓN
        // ─────────────────────────────────────────
        init() {
            this.initElements();
            this.initSidebarToggle();
            this.initActiveMenuDetection();
            this.initSubMenus();
            this.initResponsive();
            this.initLogoutModal();
            this.convertDjangoMessages(); // siempre al final
        }

        initElements() {
            this.sidebar       = document.getElementById('sidebar');
            this.sidebarToggle = document.getElementById('sidebar-toggle');
            this.adminOverlay  = document.getElementById('adminNotificationOverlay');
            this.adminCard     = document.getElementById('adminNotificationCard');
            this.logoutModal   = document.getElementById('logoutModal');
        }

        // ─────────────────────────────────────────
        // SIDEBAR
        // ─────────────────────────────────────────
        initSidebarToggle() {
            if (!this.sidebarToggle || !this.sidebar) return;
            this.sidebarToggle.addEventListener('click', () => {
                this.sidebar.classList.toggle('show');
            });
        }

        // ─────────────────────────────────────────
        // MODAL LOGOUT — reemplaza confirm() nativo
        // ─────────────────────────────────────────
        initLogoutModal() {
            if (!this.logoutModal) return;

            const confirmBtn = document.getElementById('logoutModalConfirm');
            const cancelBtn  = document.getElementById('logoutModalCancel');

            // Interceptar todos los enlaces de logout en sidebar + dropdown
            document.querySelectorAll('a[href*="logout"], a[data-logout]').forEach(link => {
                link.removeAttribute('onclick'); // quitar confirm() viejo
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const logoutUrl = link.getAttribute('href');
                    if (confirmBtn) confirmBtn.setAttribute('href', logoutUrl);
                    this._showLogoutModal();
                });
            });

            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => this._hideLogoutModal());
            }

            // ESC cierra el modal de logout
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.logoutModal.style.display === 'flex') {
                    this._hideLogoutModal();
                }
            });

            // Click fuera cierra
            this.logoutModal.addEventListener('click', (e) => {
                if (e.target === this.logoutModal) this._hideLogoutModal();
            });
        }

        _showLogoutModal() {
            if (!this.logoutModal) return;
            this.logoutModal.style.display = 'flex';
        }

        _hideLogoutModal() {
            if (!this.logoutModal) return;
            this.logoutModal.style.display = 'none';
        }

        // ─────────────────────────────────────────
        // NOTIFICACIÓN ADMIN MODAL
        // ─────────────────────────────────────────
        showAdminNotification(type, message) {
            if (!this.adminOverlay || !this.adminCard) return;

            this._clearNotification(false);

            const icon     = document.getElementById('adminNotificationIcon');
            const circle   = document.getElementById('adminNotificationCircle');
            const title    = document.getElementById('adminNotificationTitle');
            const text     = document.getElementById('adminNotificationText');
            const closeBtn = document.getElementById('adminNotificationClose');
            const progress = document.getElementById('adminNotificationProgress');

            const config = {
                success: {
                    icon:  'bi-check-circle-fill',
                    title: 'Operación Exitosa',
                    type:  'success',
                    progressColor: '#22c55e',
                },
                error: {
                    icon:  'bi-x-circle-fill',
                    title: 'Error del Sistema',
                    type:  'error',
                    progressColor: '#ef4444',
                },
                warning: {
                    icon:  'bi-exclamation-triangle-fill',
                    title: 'Advertencia',
                    type:  'warning',
                    progressColor: '#f59e0b',
                },
                info: {
                    icon:  'bi-info-circle-fill',
                    title: 'Información',
                    type:  'info',
                    progressColor: '#3b82f6',
                },
            };

            const cfg = config[type] || config.success;

            // Reset clases
            this.adminCard.className = 'admin-notification-card';
            this.adminCard.classList.add(cfg.type);
            if (circle) {
                circle.className = 'admin-notification-icon-circle';
                circle.classList.add(`circle-${cfg.type}`);
            }

            if (icon)  icon.className  = `bi ${cfg.icon}`;
            if (title) title.textContent = cfg.title;
            if (text)  text.textContent  = message;

            // Barra de progreso con el color del tipo
            if (progress) {
                progress.style.animation = 'none';
                progress.style.background = cfg.progressColor;
                void progress.offsetWidth; // reflow
                progress.style.animation = '';
            }

            // Mostrar
            this.adminOverlay.style.display = 'flex';

            // Auto-close 5s
            this._autoCloseTimer = setTimeout(() => this._clearNotification(true), 5000);

            // Botón cerrar
            if (closeBtn) closeBtn.onclick = () => this._clearNotification(true);

            // Click fuera
            this._outsideHandler = (e) => {
                if (e.target === this.adminOverlay) this._clearNotification(true);
            };
            this.adminOverlay.addEventListener('click', this._outsideHandler);

            // ESC
            this._escHandler = (e) => {
                if (e.key === 'Escape') this._clearNotification(true);
            };
            document.addEventListener('keydown', this._escHandler);
        }

        _clearNotification(hide) {
            if (this._autoCloseTimer) {
                clearTimeout(this._autoCloseTimer);
                this._autoCloseTimer = null;
            }
            if (this._escHandler) {
                document.removeEventListener('keydown', this._escHandler);
                this._escHandler = null;
            }
            if (this._outsideHandler && this.adminOverlay) {
                this.adminOverlay.removeEventListener('click', this._outsideHandler);
                this._outsideHandler = null;
            }
            if (hide && this.adminOverlay) {
                this.adminOverlay.style.display = 'none';
            }
        }

        // ─────────────────────────────────────────
        // FALLBACK TOAST — solo si no hay overlay
        // ─────────────────────────────────────────
        showToast(type, message) {
            if (typeof bootstrap === 'undefined') return;
            const toastEl = document.getElementById(`${type}Toast`);
            const msgEl   = document.getElementById(`${type}ToastMessage`);
            if (!toastEl || !msgEl) return;
            msgEl.textContent = message;
            new bootstrap.Toast(toastEl, { delay: 5000 }).show();
        }

        // ─────────────────────────────────────────
        // DJANGO MESSAGES → notificación modal
        // ─────────────────────────────────────────
        convertDjangoMessages() {
            const container = document.getElementById('django-messages');
            if (!container) return;

            const items = container.querySelectorAll('[data-message-level]');
            if (!items.length) return;

            // Mostrar solo el último mensaje
            const last  = [...items].slice(-1)[0];
            const level = last.getAttribute('data-message-level') || '';
            const text  = last.getAttribute('data-message-text')  || '';

            let type = 'success';
            if (level.includes('error') || level.includes('danger')) type = 'error';
            else if (level.includes('warning'))                        type = 'warning';
            else if (level.includes('info'))                           type = 'info';

            setTimeout(() => {
                if (this.adminOverlay) {
                    this.showAdminNotification(type, text);
                } else {
                    this.showToast(type, text);
                }
            }, 350);
        }

        // ─────────────────────────────────────────
        // MENÚ ACTIVO
        // ─────────────────────────────────────────
        initActiveMenuDetection() {
            const currentPath = window.location.pathname;
            document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
                const href = link.getAttribute('href');
                if (href && href !== '#' && currentPath.startsWith(href)) {
                    link.classList.add('active');
                }
            });
        }

        // ─────────────────────────────────────────
        // SUBMENÚS — usa eventos nativos Bootstrap
        // ─────────────────────────────────────────
        initSubMenus() {
            document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(toggle => {
                const selector = toggle.getAttribute('href') || toggle.getAttribute('data-bs-target');
                if (!selector) return;
                const target = document.querySelector(selector);
                if (!target) return;

                const chevron = toggle.querySelector('.bi-chevron-down');

                target.addEventListener('show.bs.collapse', () => {
                    if (chevron) chevron.style.transform = 'rotate(180deg)';
                });
                target.addEventListener('hide.bs.collapse', () => {
                    if (chevron) chevron.style.transform = 'rotate(0deg)';
                });
                // Estado inicial
                if (target.classList.contains('show') && chevron) {
                    chevron.style.transform = 'rotate(180deg)';
                }
            });
        }

        // ─────────────────────────────────────────
        // RESPONSIVE
        // ─────────────────────────────────────────
        initResponsive() {
            window.addEventListener('resize', () => {
                if (window.innerWidth > 768 && this.sidebar) {
                    this.sidebar.classList.remove('show');
                }
            });
        }
    }

    function init() {
        window._dashboard = new DashboardManager();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();