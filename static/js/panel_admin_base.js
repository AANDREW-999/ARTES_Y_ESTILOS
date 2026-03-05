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
            this.mainContent     = null;
            this.sidebarResizer  = null;
            this.adminOverlay    = null;
            this.adminCard       = null;
            this.logoutModal     = null;
            this._autoCloseTimer = null;
            this._escHandler     = null;
            this._outsideHandler = null;

            // Sidebar colapsable
            this._tooltips = [];
            this._flyout = null;
            this._flyoutToggle = null;
            this._flyoutCloseTimer = null;
            this._flyoutPinned = false;
            this._boundDocClick = null;
            this._boundDocKeydown = null;
            this._boundWinScroll = null;

            // Detectar si el foco viene de mouse o teclado (para no abrir flyout por click)
            this._lastInputWasPointer = false;

            // Resize state
            this._resize = {
                active: false,
                startX: 0,
                startWidth: 0,
                pointerId: null,
            };
            this.init();
        }

        // ─────────────────────────────────────────
        // INICIALIZACIÓN
        // ─────────────────────────────────────────
        init() {
            this.initElements();
            this.initSidebarCollapsible();
            this.initActiveMenuDetection();
            this.initSubMenus();
            this.initResponsive();
            this.initLogoutModal();
            this.convertDjangoMessages(); // siempre al final

            // Señales globales de interacción
            document.addEventListener('pointerdown', () => { this._lastInputWasPointer = true; }, { passive: true });
            document.addEventListener('keydown', (e) => {
                // Si el usuario navega con teclado, habilitamos apertura por focus
                if (e.key === 'Tab' || e.key.startsWith('Arrow')) this._lastInputWasPointer = false;
            });
        }

        initElements() {
            this.sidebar       = document.getElementById('sidebar');
            this.sidebarToggle = document.getElementById('sidebar-toggle');
            this.mainContent   = document.getElementById('main-content');
            this.sidebarResizer = document.getElementById('sidebar-resizer');
            this.adminOverlay  = document.getElementById('adminNotificationOverlay');
            this.adminCard     = document.getElementById('adminNotificationCard');
            this.logoutModal   = document.getElementById('logoutModal');
            this.adminCloseBtn = document.getElementById('adminNotificationClose');
            this.adminActions  = document.getElementById('adminNotificationActions');
            this.adminCancel   = document.getElementById('adminNotificationCancel');
            this.adminConfirm  = document.getElementById('adminNotificationConfirm');
        }

        // ─────────────────────────────────────────
        // SIDEBAR (colapsable desktop + offcanvas mobile)
        // ─────────────────────────────────────────
        initSidebarCollapsible() {
            if (!this.sidebarToggle || !this.sidebar) return;

            this._restoreSidebarState();
            this._restoreSidebarWidth();
            this._normalizeSidebarToggleMarkup();
            this._prepareTooltipTitles();
            this._updateSidebarModeSideEffects();
            this._initSidebarFlyout();
            this._initSidebarResize();

            this.sidebarToggle.addEventListener('click', () => {
                // Mobile: comportamiento off-canvas (show/hide)
                if (window.innerWidth <= 768) {
                    this.sidebar.classList.toggle('show');
                    return;
                }

                // Desktop: colapsar/expandir
                this._setSidebarCollapsed(!this._isSidebarCollapsed(), { persist: true });
            });
        }

        _isSidebarCollapsed() {
            return !!this.sidebar?.classList.contains('collapsed');
        }

        _restoreSidebarState() {
            const saved = localStorage.getItem('sidebarState');
            const shouldCollapse = saved === 'collapsed';
            // En móvil el modo colapsado no aplica
            if (window.innerWidth <= 768) {
                this._setSidebarCollapsed(false, { persist: false });
                return;
            }
            this._setSidebarCollapsed(shouldCollapse, { persist: false });
        }

        _restoreSidebarWidth() {
            // Solo desktop: en móvil el sidebar es off-canvas
            if (window.innerWidth <= 768) {
                this._clearSidebarWidthOverride();
                return;
            }

            const savedWidth = parseInt(localStorage.getItem('sidebarWidth') || '', 10);
            if (!Number.isFinite(savedWidth)) return;

            const clamped = this._clampSidebarWidth(savedWidth);
            document.documentElement.style.setProperty('--sidebar-width', `${clamped}px`);
        }

        _clearSidebarWidthOverride() {
            document.documentElement.style.removeProperty('--sidebar-width');
        }

        _clampSidebarWidth(width) {
            // Rango “SaaS” razonable: evita romper topbar/main
            const min = 220;
            const max = 360;
            return Math.max(min, Math.min(max, width));
        }

        _initSidebarResize() {
            if (!this.sidebarResizer || !this.sidebar) return;

            // Pointer events (mouse/touch) con captura
            this.sidebarResizer.addEventListener('pointerdown', (e) => {
                // Solo desktop y solo en modo expandido
                if (window.innerWidth <= 768) return;
                if (this._isSidebarCollapsed()) return;

                this._resize.active = true;
                this._resize.pointerId = e.pointerId;
                this._resize.startX = e.clientX;
                this._resize.startWidth = this.sidebar.getBoundingClientRect().width;

                document.body.classList.add('sidebar-resizing');

                try {
                    this.sidebarResizer.setPointerCapture(e.pointerId);
                } catch (_) {
                    // No todos los navegadores lo soportan igual
                }

                e.preventDefault();
            });

            this.sidebarResizer.addEventListener('pointermove', (e) => {
                if (!this._resize.active) return;
                if (e.pointerId !== this._resize.pointerId) return;

                const delta = e.clientX - this._resize.startX;
                const nextWidth = this._clampSidebarWidth(this._resize.startWidth + delta);
                document.documentElement.style.setProperty('--sidebar-width', `${nextWidth}px`);
            });

            const endResize = (e) => {
                if (!this._resize.active) return;
                if (e && this._resize.pointerId !== null && e.pointerId !== this._resize.pointerId) return;

                this._resize.active = false;
                this._resize.pointerId = null;
                document.body.classList.remove('sidebar-resizing');

                // Persistir ancho actual
                const current = this.sidebar.getBoundingClientRect().width;
                const clamped = this._clampSidebarWidth(current);
                localStorage.setItem('sidebarWidth', String(clamped));
            };

            this.sidebarResizer.addEventListener('pointerup', endResize);
            this.sidebarResizer.addEventListener('pointercancel', endResize);
        }

        _setSidebarCollapsed(collapsed, { persist } = { persist: true }) {
            if (!this.sidebar) return;

            this.sidebar.classList.toggle('collapsed', collapsed);
            if (this.mainContent) this.mainContent.classList.toggle('collapsed', collapsed);
            document.body.classList.toggle('sidebar-collapsed', collapsed);

            if (persist) {
                localStorage.setItem('sidebarState', collapsed ? 'collapsed' : 'expanded');
            }

            // Mantener accesibilidad: tooltips/flyouts y aria-expanded
            this._updateSidebarModeSideEffects();
        }

        _updateSidebarModeSideEffects() {
            if (!this.sidebar) return;
            const collapsed = this._isSidebarCollapsed();
            const isDesktop = window.innerWidth > 768;

            // Tooltips solo en modo colapsado
            if (collapsed) this._enableTooltips();
            else this._disableTooltips();

            // Mobile: usamos collapse nativo; Desktop: usamos flyout a la derecha
            if (!isDesktop) {
                this._closeFlyout({ restoreAria: false });
                this._syncSubmenuAriaFromCollapse();
                return;
            }

            // Desktop: el estado visual/aria lo controla el flyout
            this._forceCloseSidebarCollapsesForDesktop();
            this._resetSubmenuTogglesForFlyoutMode();
        }

        _forceCloseSidebarCollapsesForDesktop() {
            if (!this.sidebar) return;
            if (window.innerWidth <= 768) return;

            // Cerrar cualquier collapse que haya quedado abierto (por estado server-side o Bootstrap)
            this.sidebar.querySelectorAll('.collapse.show, .collapsing').forEach(el => {
                el.classList.remove('show');
                el.classList.remove('collapsing');
                el.style.height = '';
            });

            // Asegurar aria en toggles
            this.sidebar.querySelectorAll('[data-bs-toggle="collapse"]').forEach(toggle => {
                toggle.setAttribute('aria-expanded', 'false');
            });
        }

        _toggleFlyoutForToggle(toggle) {
            if (!toggle) return;
            if (!this._flyout) return;
            if (window.innerWidth <= 768) return;

            this._forceCloseSidebarCollapsesForDesktop();

            const isOpen = this._flyout.classList.contains('show');
            const isSameToggle = this._flyoutToggle === toggle;

            // Si estaba abierto por hover y el usuario hace click: “fijar” (no cerrar).
            if (isOpen && isSameToggle && !this._flyoutPinned) {
                this._flyoutPinned = true;
                return;
            }

            // Click en el mismo toggle ya fijado: cerrar.
            if (isOpen && isSameToggle && this._flyoutPinned) {
                this._closeFlyout({ restoreAria: false });
                return;
            }

            // Abrir/cambiar a otro toggle: fijar por click.
            this._flyoutPinned = true;
            this._openFlyoutForToggle(toggle);
        }

        _resetSubmenuTogglesForFlyoutMode() {
            if (!this.sidebar) return;
            this.sidebar.querySelectorAll('[data-bs-toggle="collapse"]').forEach(toggle => {
                toggle.setAttribute('aria-expanded', 'false');
                toggle.classList.remove('flyout-open');
            });
            this._closeFlyout({ restoreAria: false });
        }

        _prepareTooltipTitles() {
            if (!this.sidebar) return;
            const links = this.sidebar.querySelectorAll('.sidebar-nav .nav-link');
            links.forEach(link => {
                const hasTitle = link.getAttribute('title');
                if (hasTitle) return;

                const label = this._getNavLabel(link);
                if (!label) return;

                link.setAttribute('title', label);
                link.setAttribute('data-sidebar-title', label);
            });
        }

        _normalizeSidebarToggleMarkup() {
            if (!this.sidebar) return;
            const toggles = this.sidebar.querySelectorAll('.sidebar-nav .nav-link[data-bs-toggle="collapse"]');

            toggles.forEach(link => {
                const children = Array.from(link.children);
                const directIcon = children.find(el => el.tagName === 'I' && !el.classList.contains('bi-chevron-down') && !el.classList.contains('bi-chevron-right'));
                const directSpan = children.find(el => el.tagName === 'SPAN');
                if (directIcon || !directSpan) return;

                const iconInSpan = directSpan.querySelector('i');
                if (!iconInSpan) return;

                // Extraer icono del span para que quede como hijo directo del link
                iconInSpan.remove();
                const label = (directSpan.textContent || '').trim().replace(/\s+/g, ' ');
                directSpan.textContent = label;

                link.insertBefore(iconInSpan, directSpan);
            });
        }

        _getNavLabel(linkEl) {
            if (!linkEl) return '';
            const span = linkEl.querySelector('span');
            const raw = (span?.textContent || linkEl.textContent || '').trim();
            // Normalizar espacios
            return raw.replace(/\s+/g, ' ');
        }

        _enableTooltips() {
            if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip || !this.sidebar) return;
            if (this._tooltips.length) return;

            const links = this.sidebar.querySelectorAll('.sidebar-nav .nav-link');
            links.forEach(link => {
                const title = link.getAttribute('data-sidebar-title') || link.getAttribute('title');
                if (!title) return;

                // En colapsado, el tooltip reemplaza la falta de texto visible
                const instance = new bootstrap.Tooltip(link, {
                    placement: 'right',
                    trigger: 'hover focus',
                    container: 'body',
                    customClass: 'sidebar-tooltip',
                    boundary: 'window',
                });
                this._tooltips.push(instance);
            });
        }

        _disableTooltips() {
            if (!this._tooltips.length) return;
            this._tooltips.forEach(t => {
                try { t.dispose(); } catch (_) { /* noop */ }
            });
            this._tooltips = [];
        }

        _syncSubmenuAriaFromCollapse() {
            if (!this.sidebar) return;
            this.sidebar.querySelectorAll('[data-bs-toggle="collapse"]').forEach(toggle => {
                const selector = toggle.getAttribute('href') || toggle.getAttribute('data-bs-target');
                if (!selector) return;
                const target = document.querySelector(selector);
                if (!target) return;
                toggle.setAttribute('aria-expanded', target.classList.contains('show') ? 'true' : 'false');
            });
        }

        _initSidebarFlyout() {
            if (!this.sidebar) return;

            if (!this._flyout) {
                this._flyout = document.createElement('div');
                this._flyout.className = 'sidebar-flyout';
                this._flyout.setAttribute('aria-hidden', 'true');
                document.body.appendChild(this._flyout);

                this._flyout.addEventListener('mouseenter', () => {
                    if (this._flyoutCloseTimer) {
                        clearTimeout(this._flyoutCloseTimer);
                        this._flyoutCloseTimer = null;
                    }
                });
                this._flyout.addEventListener('mouseleave', () => {
                    if (this._flyoutPinned) return;
                    this._scheduleFlyoutClose();
                });
            }

            // Delegar comportamiento en toggles de collapse dentro del sidebar
            this.sidebar.querySelectorAll('[data-bs-toggle="collapse"]').forEach(toggle => {
                toggle.addEventListener('mouseenter', () => {
                    if (window.innerWidth <= 768) return;
                    if (this._flyoutPinned) return;
                    this._flyoutPinned = false;
                    this._openFlyoutForToggle(toggle);
                });
                toggle.addEventListener('mouseleave', () => {
                    if (window.innerWidth <= 768) return;
                    if (this._flyoutPinned) return;
                    this._scheduleFlyoutClose();
                });

                // Accesibilidad: permitir abrir con focus
                toggle.addEventListener('focusin', () => {
                    if (window.innerWidth <= 768) return;
                    // Evitar que un click (mouse) dispare el focusin y abra el flyout
                    if (this._lastInputWasPointer) return;
                    if (this._flyoutPinned) return;
                    this._flyoutPinned = false;
                    this._openFlyoutForToggle(toggle);
                });
            });

            // Desktop hard-stop: bloquear Data API de Bootstrap incluso si el handler está en document
            // (captura antes del bubbling). Esto garantiza que el click no "haga nada".
            if (!this._boundSidebarCaptureGuards) {
                this._boundSidebarCaptureGuards = {
                    click: (e) => {
                        if (window.innerWidth <= 768) return;
                        const toggle = e.target?.closest?.('[data-bs-toggle="collapse"]');
                        if (!toggle || !this.sidebar.contains(toggle)) return;
                        e.preventDefault();
                        e.stopImmediatePropagation();

                        // En desktop el click debe abrir/cerrar el flyout a la derecha
                        this._lastInputWasPointer = true;
                        this._toggleFlyoutForToggle(toggle);
                    },
                    keydown: (e) => {
                        if (window.innerWidth <= 768) return;
                        const toggle = e.target?.closest?.('[data-bs-toggle="collapse"]');
                        if (!toggle || !this.sidebar.contains(toggle)) return;
                        // Evitar que Enter/Espacio activen el collapse en desktop
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            e.stopImmediatePropagation();

                            this._lastInputWasPointer = false;
                            this._toggleFlyoutForToggle(toggle);
                        }
                    },
                };
                this.sidebar.addEventListener('click', this._boundSidebarCaptureGuards.click, true);
                this.sidebar.addEventListener('keydown', this._boundSidebarCaptureGuards.keydown, true);
            }

            // Cerrar al hacer click fuera / ESC / scroll
            if (!this._boundDocClick) {
                this._boundDocClick = (e) => {
                    if (!this._flyout?.classList.contains('show')) return;
                    const target = e.target;
                    if (this._flyout.contains(target)) return;
                    if (this.sidebar?.contains(target)) return;
                    this._closeFlyout({ restoreAria: false });
                };
                document.addEventListener('click', this._boundDocClick);
            }

            if (!this._boundDocKeydown) {
                this._boundDocKeydown = (e) => {
                    if (e.key !== 'Escape') return;
                    if (!this._flyout?.classList.contains('show')) return;
                    this._closeFlyout({ restoreAria: false });
                };
                document.addEventListener('keydown', this._boundDocKeydown);
            }

            if (!this._boundWinScroll) {
                this._boundWinScroll = () => {
                    if (!this._flyout?.classList.contains('show')) return;
                    this._closeFlyout({ restoreAria: false });
                };
                window.addEventListener('scroll', this._boundWinScroll, { passive: true });
            }
        }

        _openFlyoutForToggle(toggle) {
            if (!this._flyout || !this.sidebar) return;
            if (window.innerWidth <= 768) return;

            const selector = toggle.getAttribute('href') || toggle.getAttribute('data-bs-target');
            if (!selector) return;
            const target = document.querySelector(selector);
            if (!target) return;

            const submenu = target.querySelector('ul.nav');
            if (!submenu) return;

            // Cancelar cierre pendiente
            if (this._flyoutCloseTimer) {
                clearTimeout(this._flyoutCloseTimer);
                this._flyoutCloseTimer = null;
            }

            // Preparar contenido
            const clone = submenu.cloneNode(true);
            clone.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
            this._flyout.innerHTML = '';
            this._flyout.appendChild(clone);

            // Mostrar para medir
            this._flyout.style.visibility = 'hidden';
            this._flyout.classList.add('show');
            this._flyout.setAttribute('aria-hidden', 'false');

            const sidebarRect = this.sidebar.getBoundingClientRect();
            const toggleRect = toggle.getBoundingClientRect();
            const flyoutHeight = this._flyout.offsetHeight;

            const left = Math.round(sidebarRect.right + 4);
            let top = Math.round(toggleRect.top);

            const maxTop = window.innerHeight - flyoutHeight - 12;
            top = Math.max(8, Math.min(top, maxTop));

            this._flyout.style.left = `${left}px`;
            this._flyout.style.top = `${top}px`;
            this._flyout.style.visibility = 'visible';

            // Accesibilidad
            this._setToggleAriaExpanded(toggle, true);
            if (this._flyoutToggle && this._flyoutToggle !== toggle) {
                this._setToggleAriaExpanded(this._flyoutToggle, false);
                this._flyoutToggle.classList.remove('flyout-open');
            }
            toggle.classList.add('flyout-open');
            this._flyoutToggle = toggle;
        }

        _scheduleFlyoutClose() {
            if (this._flyoutCloseTimer) clearTimeout(this._flyoutCloseTimer);
            if (this._flyoutPinned) return;
            this._flyoutCloseTimer = setTimeout(() => {
                this._closeFlyout({ restoreAria: false });
            }, 240);
        }

        _closeFlyout({ restoreAria } = { restoreAria: false }) {
            if (!this._flyout) return;
            if (this._flyoutCloseTimer) {
                clearTimeout(this._flyoutCloseTimer);
                this._flyoutCloseTimer = null;
            }

            if (this._flyoutToggle) {
                this._flyoutToggle.classList.remove('flyout-open');
                if (restoreAria) {
                    const selector = this._flyoutToggle.getAttribute('href') || this._flyoutToggle.getAttribute('data-bs-target');
                    const target = selector ? document.querySelector(selector) : null;
                    this._setToggleAriaExpanded(this._flyoutToggle, !!target?.classList.contains('show'));
                } else {
                    this._setToggleAriaExpanded(this._flyoutToggle, false);
                }
            }

            this._flyout.classList.remove('show');
            this._flyout.setAttribute('aria-hidden', 'true');
            this._flyout.innerHTML = '';
            this._flyoutToggle = null;
            this._flyoutPinned = false;
        }

        _setToggleAriaExpanded(toggle, expanded) {
            if (!toggle) return;
            toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
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
                    if (confirmBtn) {
                        confirmBtn.setAttribute('href', logoutUrl);
                        confirmBtn.addEventListener('click', () => {
                            window.location.href = logoutUrl;
                        }, { once: true }); // Asegurar que el evento se ejecute solo una vez
                    }
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
                progress.style.display = '';
            }

            if (this.adminActions) this.adminActions.style.display = 'none';
            if (closeBtn) closeBtn.style.display = '';

            // Mostrar
            this.adminOverlay.style.display = 'flex';

            // Auto-close 10s
            this._autoCloseTimer = setTimeout(() => this._clearNotification(true), 10000);

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

        showAdminConfirm(type, message, onConfirm, onCancel) {
            if (!this.adminOverlay || !this.adminCard) return;

            this._clearNotification(false);

            const icon     = document.getElementById('adminNotificationIcon');
            const circle   = document.getElementById('adminNotificationCircle');
            const title    = document.getElementById('adminNotificationTitle');
            const text     = document.getElementById('adminNotificationText');
            const progress = document.getElementById('adminNotificationProgress');

            const config = {
                success: { icon: 'bi-check-circle-fill', title: 'Confirmacion', type: 'success', progressColor: '#22c55e' },
                error:   { icon: 'bi-x-circle-fill', title: 'Confirmacion', type: 'error', progressColor: '#ef4444' },
                warning: { icon: 'bi-exclamation-triangle-fill', title: 'Advertencia', type: 'warning', progressColor: '#f59e0b' },
                info:    { icon: 'bi-info-circle-fill', title: 'Confirmacion', type: 'info', progressColor: '#3b82f6' },
            };

            const cfg = config[type] || config.warning;

            this.adminCard.className = 'admin-notification-card';
            this.adminCard.classList.add(cfg.type);
            if (circle) {
                circle.className = 'admin-notification-icon-circle';
                circle.classList.add(`circle-${cfg.type}`);
            }
            if (icon)  icon.className  = `bi ${cfg.icon}`;
            if (title) title.textContent = cfg.title;
            if (text)  text.textContent  = message;

            if (progress) progress.style.display = 'none';
            if (this.adminActions) this.adminActions.style.display = 'flex';
            if (this.adminCloseBtn) this.adminCloseBtn.style.display = 'none';

            this.adminOverlay.style.display = 'flex';

            if (this.adminConfirm) {
                this.adminConfirm.onclick = () => {
                    this._clearNotification(true);
                    if (typeof onConfirm === 'function') onConfirm();
                };
            }

            if (this.adminCancel) {
                this.adminCancel.onclick = () => {
                    this._clearNotification(true);
                    if (typeof onCancel === 'function') onCancel();
                };
            }

            this._outsideHandler = (e) => {
                if (e.target === this.adminOverlay) {
                    this._clearNotification(true);
                    if (typeof onCancel === 'function') onCancel();
                }
            };
            this.adminOverlay.addEventListener('click', this._outsideHandler);

            this._escHandler = (e) => {
                if (e.key === 'Escape') {
                    this._clearNotification(true);
                    if (typeof onCancel === 'function') onCancel();
                }
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
            if (this.adminActions) this.adminActions.style.display = 'none';
            if (this.adminCloseBtn) this.adminCloseBtn.style.display = '';
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
                if (!this.adminOverlay) {
                    this.showToast(type, text);
                    return;
                }

                if (level.includes('field-inactive')) {
                    this.showAdminNotification('warning', text);
                    const closeBtn = document.getElementById('adminNotificationClose');
                    const overlay = document.getElementById('adminNotificationOverlay');
                    const indexUrl = overlay?.dataset?.indexUrl;
                    if (closeBtn) {
                        closeBtn.textContent = 'Volver al inicio';
                        closeBtn.onclick = () => {
                            if (indexUrl) window.location.href = indexUrl;
                        };
                    }
                    if (indexUrl) {
                        setTimeout(() => {
                            window.location.href = indexUrl;
                        }, 3500);
                    }
                    return;
                }

                this.showAdminNotification(type, text);
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

                const chevron = toggle.querySelector('.bi-chevron-right, .bi-chevron-down');

                target.addEventListener('show.bs.collapse', () => {
                    if (chevron && chevron.classList.contains('bi-chevron-down')) chevron.style.transform = 'rotate(180deg)';
                    if (chevron && chevron.classList.contains('bi-chevron-right')) chevron.style.transform = 'rotate(90deg)';
                });
                target.addEventListener('hide.bs.collapse', () => {
                    if (chevron) chevron.style.transform = 'rotate(0deg)';
                });
                // Estado inicial
                if (target.classList.contains('show') && chevron) {
                    if (chevron.classList.contains('bi-chevron-down')) chevron.style.transform = 'rotate(180deg)';
                    if (chevron.classList.contains('bi-chevron-right')) chevron.style.transform = 'rotate(90deg)';
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

                // En cambios de breakpoint, re-evaluar el estado colapsado
                if (window.innerWidth <= 768) {
                    this._setSidebarCollapsed(false, { persist: false });
                    this._closeFlyout({ restoreAria: false });
                    this._clearSidebarWidthOverride();
                } else {
                    this._restoreSidebarState();
                    this._restoreSidebarWidth();
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