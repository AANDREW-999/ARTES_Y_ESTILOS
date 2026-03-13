(function () {
    'use strict';

    function getCsrfToken() {
        const name = 'csrftoken=';
        const cookie = document.cookie
            .split(';')
            .map((part) => part.trim())
            .find((part) => part.startsWith(name));
        return cookie ? decodeURIComponent(cookie.slice(name.length)) : '';
    }

    function hideDot() {
        const dot = document.getElementById('adminNotificationsDot');
        if (dot) dot.classList.add('is-hidden');
    }

    function initNotificationsDropdown() {
        const dropdown = document.getElementById('adminNotificationsDropdown');
        if (!dropdown) return;

        const triggerButton = document.getElementById('adminNotificationsButton');
        const menu = dropdown.querySelector('.admin-notifications-menu');
        const list = document.getElementById('adminNotificationsList');
        const readUrl = dropdown.getAttribute('data-read-url');
        if (!readUrl) return;

        const markButton = document.getElementById('adminMarkNotificationsRead');
        const toggleAllButton = document.getElementById('adminToggleAllNotifications');
        let alreadyMarked = false;

        const setOpen = (open) => {
            if (!menu || !triggerButton) return;
            dropdown.classList.toggle('is-open', open);
            menu.classList.toggle('show', open);
            triggerButton.setAttribute('aria-expanded', open ? 'true' : 'false');
            triggerButton.setAttribute('title', open ? 'Cerrar notificaciones' : 'Abrir notificaciones');

            if (!open && toggleAllButton) {
                dropdown.classList.remove('is-expanded');
                toggleAllButton.textContent = 'Ver todas';
            }
        };

        const markAsRead = async () => {
            try {
                await fetch(readUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify({ action: 'mark_all_read' }),
                });
                hideDot();
                alreadyMarked = true;
            } catch (_) {
                // Si falla la llamada, no rompemos el flujo visual del panel.
            }
        };

        if (triggerButton && menu) {
            triggerButton.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                const willOpen = !dropdown.classList.contains('is-open');
                setOpen(willOpen);
                if (willOpen && !alreadyMarked) {
                    markAsRead();
                }
            });

            document.addEventListener('click', (event) => {
                if (!dropdown.contains(event.target)) {
                    setOpen(false);
                }
            });

            document.addEventListener('keydown', (event) => {
                if (event.key === 'Escape') {
                    setOpen(false);
                }
            });

            // Estado inicial del tooltip
            triggerButton.setAttribute('title', 'Abrir notificaciones');
        }

        if (markButton) {
            markButton.addEventListener('click', (event) => {
                event.preventDefault();
                markAsRead();
            });
        }

        if (toggleAllButton && list) {
            toggleAllButton.addEventListener('click', (event) => {
                event.preventDefault();
                const expanded = dropdown.classList.toggle('is-expanded');
                toggleAllButton.textContent = expanded ? 'Ver menos' : 'Ver todas';
            });
        }
    }

    document.addEventListener('DOMContentLoaded', initNotificationsDropdown);
})();
