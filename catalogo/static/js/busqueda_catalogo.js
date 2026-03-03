document.addEventListener('DOMContentLoaded', function () {

    const searchInput = document.querySelector('.search-input');
    const tabla       = document.querySelector('.catalogo-table tbody');

    if (!searchInput || !tabla) return;

    searchInput.addEventListener('input', function () {
        const termino = this.value.trim().toLowerCase();
        const filas   = tabla.querySelectorAll('tr');

        filas.forEach(function (fila) {
            // Ignorar fila de estado vacío
            if (fila.querySelector('.empty-state')) return;

            // Columnas a buscar: producto (0), categoría (1), tamaño (2)
            const nombre    = fila.cells[0]?.textContent.toLowerCase() || '';
            const categoria = fila.cells[1]?.textContent.toLowerCase() || '';
            const tamano    = fila.cells[2]?.textContent.toLowerCase() || '';

            const coincide = nombre.includes(termino)
                          || categoria.includes(termino)
                          || tamano.includes(termino);

            fila.style.display = coincide ? '' : 'none';
        });

        // Mostrar mensaje si ninguna fila coincide
        const visibles = Array.from(filas).filter(f =>
            !f.querySelector('.empty-state') && f.style.display !== 'none'
        );

        let sinResultados = tabla.querySelector('.fila-sin-resultados');
        if (visibles.length === 0 && termino !== '') {
            if (!sinResultados) {
                sinResultados = document.createElement('tr');
                sinResultados.className = 'fila-sin-resultados';
                sinResultados.innerHTML = `
                    <td colspan="7">
                        <div class="empty-state">
                            <i class="bi bi-search"></i>
                            <p>No se encontraron productos que coincidan con "<strong>${termino}</strong>".</p>
                        </div>
                    </td>`;
                tabla.appendChild(sinResultados);
            } else {
                sinResultados.querySelector('strong').textContent = termino;
                sinResultados.style.display = '';
            }
        } else if (sinResultados) {
            sinResultados.style.display = 'none';
        }
    });

});