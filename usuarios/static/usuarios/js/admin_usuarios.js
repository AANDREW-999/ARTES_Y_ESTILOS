/**
 * JavaScript para el Sistema de Administración de Usuarios
 * Mejoras de UX y animaciones
 */

document.addEventListener('DOMContentLoaded', function() {

    // ==========================================
    // CONFIRMACIONES DE ACCIONES
    // ==========================================

    // Confirmación para desactivar usuario
    const desactivarButtons = document.querySelectorAll('.btn-desactivar');
    desactivarButtons.forEach(btn => {
        if (!btn.closest('form')) { // Solo agregar si no está dentro de un form de confirmación
            btn.addEventListener('click', function(e) {
                const username = this.getAttribute('data-username');
                if (username) {
                    const confirmed = confirm(`¿Estás seguro de desactivar al usuario ${username}?`);
                    if (!confirmed) {
                        e.preventDefault();
                    }
                }
            });
        }
    });

    // ==========================================
    // ANIMACIONES EN HOVER
    // ==========================================

    // Efecto parallax suave en tarjetas
    const cards = document.querySelectorAll('.stat-card, .profile-header-card, .profile-info-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
        });
    });

    // ==========================================
    // BÚSQUEDA EN TIEMPO REAL (opcional)
    // ==========================================

    const searchInput = document.getElementById('search-usuarios');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = document.querySelectorAll('.usuarios-table tbody tr');

            rows.forEach(row => {
                const username = row.querySelector('.usuario-info strong')?.textContent.toLowerCase() || '';
                const email = row.cells[1]?.textContent.toLowerCase() || '';

                if (username.includes(filter) || email.includes(filter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // ==========================================
    // TOOLTIPS MEJORADOS
    // ==========================================

    // Inicializar tooltips de Bootstrap si están disponibles
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // ==========================================
    // ANIMACIÓN AL CARGAR
    // ==========================================

    // Animar estadísticas al cargar
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach((stat, index) => {
        const finalValue = parseInt(stat.textContent);
        stat.textContent = '0';

        setTimeout(() => {
            animateValue(stat, 0, finalValue, 800);
        }, index * 100);
    });

    function animateValue(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // ==========================================
    // VALIDACIÓN DE FORMULARIOS
    // ==========================================

    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // ==========================================
    // PREVIEW DE IMAGEN DE PERFIL
    // ==========================================

    const fotoInput = document.querySelector('input[type="file"][name*="foto"]');
    if (fotoInput) {
        fotoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const preview = document.querySelector('.profile-avatar, .profile-avatar-placeholder');
                    if (preview) {
                        if (preview.tagName === 'IMG') {
                            preview.src = event.target.result;
                        } else {
                            const img = document.createElement('img');
                            img.src = event.target.result;
                            img.className = 'profile-avatar';
                            preview.replaceWith(img);
                        }
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ==========================================
    // COPIAR INFORMACIÓN AL PORTAPAPELES
    // ==========================================

    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Mostrar feedback
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check"></i> Copiado';
                this.classList.add('btn-success');

                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                }, 2000);
            });
        });
    });

    // ==========================================
    // SCROLL SUAVE
    // ==========================================

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // ==========================================
    // DETECCIÓN DE CAMBIOS NO GUARDADOS
    // ==========================================

    let formChanged = false;
    const editForms = document.querySelectorAll('form[method="post"]');

    editForms.forEach(form => {
        // Solo para formularios de edición
        if (form.querySelector('input[type="text"], textarea, select')) {
            const inputs = form.querySelectorAll('input, textarea, select');

            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    formChanged = true;
                });
            });

            form.addEventListener('submit', () => {
                formChanged = false;
            });
        }
    });

    window.addEventListener('beforeunload', (e) => {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = '¿Estás seguro de salir? Los cambios no guardados se perderán.';
        }
    });

    // ==========================================
    // EFECTO DE CARGA COMPLETADA
    // ==========================================

    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 100);

    console.log('✅ Sistema de administración de usuarios cargado correctamente');
});

