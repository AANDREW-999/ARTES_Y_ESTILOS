document.addEventListener('DOMContentLoaded', function () {
    const normalize = (value) => (value || '')
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');

    const searchInputs = document.querySelectorAll('.js-live-search');
    if (!searchInputs.length) return;

    searchInputs.forEach(function (searchInput) {
        const targetSelector = searchInput.dataset.target;
        if (!targetSelector) return;

        const counterSelector = searchInput.dataset.counter;
        const counterEl = counterSelector ? document.querySelector(counterSelector) : null;

        const tabla = document.querySelector(targetSelector);
        if (!tabla) return;

        const dataRows = Array.from(tabla.querySelectorAll('tr[data-search-row="1"]'));
        const serverEmptyRow = tabla.querySelector('tr[data-empty-server="1"]');

        const headerColumns = tabla.closest('table')?.querySelectorAll('thead th')?.length || 1;

        const ensureClientEmptyRow = () => {
            let row = tabla.querySelector('tr.js-empty-client');
            if (row) return row;

            row = document.createElement('tr');
            row.className = 'js-empty-client';
            row.style.display = 'none';
            row.innerHTML = `
                <td colspan="${headerColumns}">
                    <div class="empty-state">
                        <i class="bi bi-search"></i>
                        <p>No hay coincidencias para "<strong></strong>".</p>
                    </div>
                </td>
            `;
            tabla.appendChild(row);
            return row;
        };

        const clientEmptyRow = ensureClientEmptyRow();

        const updateCounter = (count) => {
            if (counterEl) {
                counterEl.textContent = String(count);
            }
        };

        // Valor inicial de resultados visibles al cargar la pagina.
        updateCounter(dataRows.length);

        searchInput.addEventListener('input', function () {
            const termRaw = this.value.trim();
            const term = normalize(termRaw);

            if (serverEmptyRow) {
                serverEmptyRow.style.display = term ? 'none' : '';
            }

            let visibles = 0;

            dataRows.forEach(function (fila) {
                const text = normalize(fila.dataset.searchText || fila.textContent);
                const match = !term || text.includes(term);
                fila.style.display = match ? '' : 'none';
                if (match) visibles += 1;
            });

            if (term && visibles === 0 && dataRows.length > 0) {
                clientEmptyRow.style.display = '';
                const strong = clientEmptyRow.querySelector('strong');
                if (strong) strong.textContent = termRaw;
            } else {
                clientEmptyRow.style.display = 'none';
            }

            updateCounter(visibles);
        });
    });
});