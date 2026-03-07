/**
 * PERFIL.JS - Sistema de validación con toasts
 * Validación en tiempo real y notificaciones elegantes
 * @version 1.0
 * @date 2026-02-20
 */

(function() {
    'use strict';

    class PerfilValidator {
        constructor() {
            this.toasts = {
                success: null,
                error: null,
                warning: null
            };
        }

        initialize() {
            console.log('🚀 Iniciando validador de perfil...');

            if (typeof bootstrap === 'undefined') {
                console.error('❌ Bootstrap no está cargado');
                return;
            }

            this.initializeToasts();
            this.convertDjangoMessages();
            this.bindFormValidation();
            this.bindRealTimeValidation();
            this.previewAvatar();

            console.log('✅ Validador de perfil iniciado');
        }

        // ================================================================
        // TOASTS BOOTSTRAP
        // ================================================================
        initializeToasts() {
            this.toasts.success = document.getElementById('successToast');
            this.toasts.error = document.getElementById('errorToast');
            this.toasts.warning = document.getElementById('warningToast');

            if (this.toasts.success) this.toasts.success = new bootstrap.Toast(this.toasts.success);
            if (this.toasts.error) this.toasts.error = new bootstrap.Toast(this.toasts.error);
            if (this.toasts.warning) this.toasts.warning = new bootstrap.Toast(this.toasts.warning);
        }

        showToast(type, message) {
            const toastElement = document.getElementById(`${type}Toast`);
            const messageElement = document.getElementById(`${type}ToastMessage`);

            if (toastElement && messageElement && this.toasts[type]) {
                messageElement.textContent = message;
                this.toasts[type].show();
            }
        }

        // ================================================================
        // CONVERTIR MENSAJES DJANGO A TOASTS
        // ================================================================
        convertDjangoMessages() {
            const messagesContainer = document.getElementById('django-messages');
            if (!messagesContainer) return;

            const messages = messagesContainer.querySelectorAll('[data-message-level]');
            messages.forEach(msg => {
                const level = msg.getAttribute('data-message-level');
                const text = msg.getAttribute('data-message-text');

                let type = 'success';
                if (level.includes('error') || level.includes('danger')) type = 'error';
                else if (level.includes('warning')) type = 'warning';

                setTimeout(() => this.showToast(type, text), 100);
            });
        }

        // ================================================================
        // VALIDACIÓN EN TIEMPO REAL
        // ================================================================
        bindRealTimeValidation() {
            const form = document.querySelector('form');
            if (!form) return;

            // Validar username
            const usernameInput = document.getElementById('id_username');
            if (usernameInput) {
                usernameInput.addEventListener('blur', () => this.validateUsername(usernameInput));
                usernameInput.addEventListener('input', () => {
                    if (usernameInput.classList.contains('error')) {
                        this.validateUsername(usernameInput);
                    }
                });
            }

            // Validar email
            const emailInput = document.getElementById('id_email');
            if (emailInput) {
                emailInput.addEventListener('blur', () => this.validateEmail(emailInput));
                emailInput.addEventListener('input', () => {
                    if (emailInput.classList.contains('error')) {
                        this.validateEmail(emailInput);
                    }
                });
            }

            // Validar teléfono
            const phoneInput = document.getElementById('id_telefono');
            if (phoneInput) {
                phoneInput.addEventListener('input', (e) => {
                    // Solo números y espacios
                    e.target.value = e.target.value.replace(/[^\d\s\-+()]/g, '');
                });
            }

            // Validar nombres
            const firstNameInput = document.getElementById('id_first_name');
            const lastNameInput = document.getElementById('id_last_name');

            [firstNameInput, lastNameInput].forEach(input => {
                if (input) {
                    input.addEventListener('input', (e) => {
                        // Solo letras y espacios
                        e.target.value = e.target.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
                    });
                }
            });
        }

        validateUsername(input) {
            const value = input.value.trim();
            const errorDiv = this.getOrCreateErrorDiv(input);

            if (!value) {
                this.setFieldError(input, errorDiv, 'El nombre de usuario es obligatorio');
                return false;
            }

            if (value.length < 4) {
                this.setFieldError(input, errorDiv, 'Mínimo 4 caracteres');
                return false;
            }

            if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
                this.setFieldError(input, errorDiv, 'Solo letras, números, guiones y guiones bajos');
                return false;
            }

            this.clearFieldError(input, errorDiv);
            return true;
        }

        validateEmail(input) {
            const value = input.value.trim();
            const errorDiv = this.getOrCreateErrorDiv(input);

            if (!value) {
                this.setFieldError(input, errorDiv, 'El correo electrónico es obligatorio');
                return false;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                this.setFieldError(input, errorDiv, 'Formato de correo inválido');
                return false;
            }

            this.clearFieldError(input, errorDiv);
            return true;
        }

        setFieldError(input, errorDiv, message) {
            input.classList.add('error');
            input.classList.add('form-input-futurista');
            errorDiv.textContent = message;
            errorDiv.style.display = 'flex';
        }

        clearFieldError(input, errorDiv) {
            input.classList.remove('error');
            errorDiv.style.display = 'none';
        }

        getOrCreateErrorDiv(input) {
            let errorDiv = input.parentElement.querySelector('.form-error-message');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'form-error-message';
                errorDiv.innerHTML = '<i class="bi bi-exclamation-circle"></i> <span></span>';
                input.parentElement.appendChild(errorDiv);
            }
            return errorDiv.querySelector('span') || errorDiv;
        }

        // ================================================================
        // VALIDACIÓN AL ENVIAR FORMULARIO
        // ================================================================
        bindFormValidation() {
            const form = document.querySelector('form');
            if (!form) return;

            form.addEventListener('submit', (e) => {
                console.log('📝 Validando formulario de perfil...');

                let hasErrors = false;
                const errors = [];

                // Validar username
                const usernameInput = document.getElementById('id_username');
                if (usernameInput && !this.validateUsername(usernameInput)) {
                    hasErrors = true;
                    errors.push('Nombre de usuario inválido');
                }

                // Validar email
                const emailInput = document.getElementById('id_email');
                if (emailInput && !this.validateEmail(emailInput)) {
                    hasErrors = true;
                    errors.push('Correo electrónico inválido');
                }

                // Validar nombres
                const firstNameInput = document.getElementById('id_first_name');
                if (firstNameInput && !firstNameInput.value.trim()) {
                    hasErrors = true;
                    errors.push('El nombre es obligatorio');
                    firstNameInput.classList.add('error');
                }

                const lastNameInput = document.getElementById('id_last_name');
                if (lastNameInput && !lastNameInput.value.trim()) {
                    hasErrors = true;
                    errors.push('El apellido es obligatorio');
                    lastNameInput.classList.add('error');
                }

                if (hasErrors) {
                    e.preventDefault();
                    this.showToast('error', errors[0]);

                    // Scroll al primer error
                    const firstError = form.querySelector('.error');
                    if (firstError) {
                        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        firstError.focus();
                    }

                    console.log('❌ Formulario con errores:', errors);
                    return false;
                }

                console.log('✅ Formulario válido, enviando...');
                this.showToast('success', 'Guardando cambios...');
                return true;
            });
        }

        // ================================================================
        // PREVIEW DE AVATAR
        // ================================================================
        previewAvatar() {
            const avatarInput = document.getElementById('id_foto_perfil');
            if (!avatarInput) return;

            avatarInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (!file) return;

                // Validar tipo de archivo
                if (!file.type.startsWith('image/')) {
                    this.showToast('error', 'Por favor selecciona una imagen válida');
                    avatarInput.value = '';
                    return;
                }

                // Validar tamaño (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    this.showToast('error', 'La imagen no debe superar 5MB');
                    avatarInput.value = '';
                    return;
                }

                // Mostrar preview
                const reader = new FileReader();
                reader.onload = (e) => {
                    const preview = document.querySelector('.perfil-avatar-large, .perfil-avatar-placeholder');
                    if (preview) {
                        if (preview.tagName === 'IMG') {
                            preview.src = e.target.result;
                        } else {
                            const img = document.createElement('img');
                            img.src = e.target.result;
                            img.className = 'perfil-avatar-large';
                            preview.replaceWith(img);
                        }
                        this.showToast('success', 'Vista previa cargada');
                    }
                };
                reader.readAsDataURL(file);
            });
        }
    }

    // ================================================================
    // INICIALIZACIÓN
    // ================================================================
    function init() {
        const validator = new PerfilValidator();
        validator.initialize();

        // Agregar clases futuristas a inputs del formulario
        document.querySelectorAll('input[type="text"], input[type="email"], input[type="date"], input[type="tel"], textarea, select').forEach(input => {
            if (!input.classList.contains('form-input-futurista')) {
                input.classList.add('form-input-futurista');
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

