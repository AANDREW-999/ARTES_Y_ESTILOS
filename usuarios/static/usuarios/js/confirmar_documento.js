document.addEventListener('DOMContentLoaded', function () {
    const docInput      = document.getElementById('id_documento');
    const docOriginal   = document.getElementById('documento-original')?.value || '';
    const confirmDiv    = document.getElementById('confirmacion-documento');
    const docNuevoEl    = document.getElementById('doc-nuevo-texto');
    const checkBox      = document.getElementById('check-confirmar-documento');
    const confirmInput  = document.getElementById('confirmar_cambio_documento');
    const form          = document.getElementById('form-editar-usuario');
    const isActiveChk   = document.getElementById('id_is_active');
    const esAutoEdicion = document.body.dataset.esAutoEdicion === 'true';

    // Proteger auto-desactivación
    if (isActiveChk && esAutoEdicion) {
        isActiveChk.checked = true;
        isActiveChk.addEventListener('change', function () {
            if (!this.checked) {
                this.checked = true;
                window._dashboard?.showAdminNotification('warning', 'No puedes desactivar tu propia cuenta.');
            }
        });
    }

    // Cambio de documento → mostrar confirmación
    docInput?.addEventListener('input', function () {
        const val = this.value.trim();
        if (val && val !== docOriginal) {
            confirmDiv.style.display = 'block';
            docNuevoEl.textContent = val;
            confirmDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            confirmDiv.style.display = 'none';
            if (checkBox) checkBox.checked = false;
            if (confirmInput) confirmInput.value = '';
        }
    });

    // Validar al enviar
    form?.addEventListener('submit', function (e) {
        const val = docInput?.value.trim() || '';
        if (val && val !== docOriginal) {
            if (!checkBox?.checked) {
                e.preventDefault();
                window._dashboard?.showAdminNotification('warning', 'Marca la casilla de confirmación para cambiar el documento.');
                checkBox?.focus();
                return;
            }
            if (confirmInput?.value !== 'CONFIRMAR') {
                e.preventDefault();
                window._dashboard?.showAdminNotification('warning', 'Escribe exactamente "CONFIRMAR" para autorizar el cambio.');
                confirmInput?.focus();
                return;
            }
        }
        if (esAutoEdicion && isActiveChk && !isActiveChk.checked) {
            e.preventDefault();
            isActiveChk.checked = true;
            window._dashboard?.showAdminNotification('error', 'No puedes desactivar tu propia cuenta.');
        }
    });

    // Scroll al primer error al cargar
    const firstError = document.querySelector('.field-input--error');
    if (firstError) {
        setTimeout(() => firstError.scrollIntoView({ behavior: 'smooth', block: 'center' }), 150);
        firstError.focus();
    }
});