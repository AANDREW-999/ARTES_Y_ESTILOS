document.addEventListener('DOMContentLoaded', function () {
    const moneyInputs = document.querySelectorAll('.js-money-input');
    if (!moneyInputs.length) {
        return;
    }

    function parseFlexible(rawValue) {
        const raw = String(rawValue || '').trim();
        if (!raw) return null;

        // Caso local: 1.234.567,89
        if (raw.includes(',')) {
            const normalized = raw.replace(/\./g, '').replace(',', '.');
            const num = Number(normalized);
            return Number.isFinite(num) ? num : null;
        }

        // Caso simple: 1234567 o 1234567.89
        const num = Number(raw);
        return Number.isFinite(num) ? num : null;
    }

    function formatMoney(num) {
        return num.toLocaleString('es-CO', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    function normalizeForSubmit(rawValue) {
        const num = parseFlexible(rawValue);
        if (num === null) return '';
        return num.toFixed(2);
    }

    moneyInputs.forEach(function (input) {
        if (input.value) {
            const parsed = parseFlexible(input.value);
            if (parsed !== null) {
                input.value = formatMoney(parsed);
            }
        }

        input.addEventListener('input', function () {
            const clean = this.value.replace(/[^\d,\.]/g, '');
            this.value = clean;
        });

        input.addEventListener('blur', function () {
            const parsed = parseFlexible(this.value);
            this.value = parsed === null ? '' : formatMoney(parsed);
        });
    });

    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            moneyInputs.forEach(function (input) {
                input.value = normalizeForSubmit(input.value);
            });
        });
    });
});
