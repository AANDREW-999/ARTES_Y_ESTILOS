document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('productos-container');
    const itemPickerPanel = document.getElementById('itemPickerPanel');
    const itemPickerGrid = document.getElementById('itemPickerGrid');
    let activePickerItem = null;

    const fechaInput = document.getElementById('fecha_emision') || document.getElementById('id_fecha_emision');
    if (fechaInput && !String(fechaInput.value || '').trim()) {
        const hoy = new Date();
        const year = hoy.getFullYear();
        const month = String(hoy.getMonth() + 1).padStart(2, '0');
        const day = String(hoy.getDate()).padStart(2, '0');
        fechaInput.value = `${year}-${month}-${day}`;
    }

    function limpiarNumero(valor) {
        if (!valor) return '';
        return String(valor).replace(/[^\d.]/g, '');
    }

    function formatearMiles(valor) {
        if (!valor) return '';
        const partes = String(valor).split('.');
        const entero = partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return partes.length > 1 ? `${entero},${partes[1]}` : entero;
    }

    function parsearNumero(valor) {
        if (!valor) return 0;
        return parseFloat(String(valor).replace(/\./g, '').replace(',', '.')) || 0;
    }

    function parsearPrecioData(valor) {
        if (!valor) return 0;
        const str = String(valor).trim();
        if (!str) return 0;
        if (str.includes(',')) {
            return parseFloat(str.replace(/\./g, '').replace(',', '.')) || 0;
        }
        return parseFloat(str) || 0;
    }

    function getStockClass(stockRaw) {
        const stock = parseInt(stockRaw, 10) || 0;
        if (stock <= 5) return 'stock-low text-danger';
        if (stock <= 15) return 'stock-medium text-warning';
        return 'stock-high text-success';
    }

    function escapeHtml(str) {
        return String(str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function cardMarkupFromOption(option) {
        const nombre = (option.textContent || '').replace(/\(Stock:.*\)/i, '').trim() || 'Item';
        const tipo = option.getAttribute('data-tipo') || 'Item';
        const stock = option.getAttribute('data-stock') || '0';
        const imagen = option.getAttribute('data-imagen') || '';
        const stockClass = getStockClass(stock);
        const stockTexto = `Stock ${stock}`;
        const thumb = imagen
            ? `<img src="${escapeHtml(imagen)}" alt="${escapeHtml(nombre)}" class="item-picker-thumb">`
            : `<span class="item-picker-thumb-fallback">${escapeHtml(nombre.slice(0, 2).toUpperCase())}</span>`;

        return `
            <div class="item-picker-card">
                ${thumb}
                <div class="item-picker-meta">
                    <strong>${escapeHtml(nombre)}</strong>
                    <span class="item-type">${escapeHtml(tipo)}</span>
                    <span class="stock-indicator ${stockClass}">${escapeHtml(stockTexto)}</span>
                </div>
            </div>
        `;
    }

    function autocompletarPrecioItem(item, forzar) {
        if (!item) return;
        const itemSelect = item.querySelector('.item-select');
        const precioInput = item.querySelector('.precio-input');
        if (!itemSelect || !precioInput) return;

        const selectedOption = itemSelect.options[itemSelect.selectedIndex];
        const precioRaw = selectedOption ? selectedOption.getAttribute('data-precio') : null;
        const precioNum = parsearPrecioData(precioRaw);
        const precioActual = parsearNumero(precioInput.value);

        if (precioNum > 0 && (forzar || !precioActual || precioActual <= 0)) {
            precioInput.value = formatearMiles(precioNum.toFixed(2));
        } else if (forzar && !precioNum) {
            precioInput.value = '';
        }

        actualizarPreview(item);
        calcularTotales();
    }

    function bloquearFlechas(input) {
        input.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                e.preventDefault();
            }
        });
        input.addEventListener('wheel', function (e) {
            e.preventDefault();
        }, { passive: false });
    }

    function aplicarFormatoMiles(input) {
        bloquearFlechas(input);

        input.addEventListener('input', function () {
            const pos = this.selectionStart;
            const valorPrevio = this.value;

            let limpio = limpiarNumero(this.value);
            const partes = limpio.split('.');
            if (partes.length > 2) limpio = partes[0] + '.' + partes.slice(1).join('');

            this.value = formatearMiles(limpio);

            const diff = this.value.length - valorPrevio.length;
            this.setSelectionRange(pos + diff, pos + diff);

            calcularTotales();
        });

        input.addEventListener('blur', function () {
            const num = parsearNumero(this.value);
            this.value = num > 0 ? formatearMiles(num.toFixed(2)) : '';
        });
    }

    function renderPickerFor(item) {
        if (!itemPickerPanel || !itemPickerGrid) return;
        const select = item.querySelector('.item-select');
        if (!select) return;

        itemPickerGrid.innerHTML = '';
        Array.from(select.options).forEach((option) => {
            if (!option.value) return;

            const card = document.createElement('button');
            card.type = 'button';
            card.className = 'item-picker-option';
            card.innerHTML = cardMarkupFromOption(option);
            card.addEventListener('click', function () {
                select.value = option.value;
                select.dispatchEvent(new Event('change', { bubbles: true }));
                itemPickerPanel.classList.add('d-none');
                activePickerItem = null;
            });
            itemPickerGrid.appendChild(card);
        });
    }

    function actualizarPreview(item) {
        const select = item.querySelector('.item-select');
        const preview = item.querySelector('.item-selected-preview');
        const previewContent = preview ? preview.querySelector('.item-selected-content') : null;
        const triggerBtn = item.querySelector('.item-picker-trigger');
        if (!select || !preview || !previewContent || !triggerBtn) return;

        const selected = select.options[select.selectedIndex];
        if (!selected || !selected.value) {
            preview.classList.add('d-none');
            previewContent.innerHTML = '';
            triggerBtn.classList.remove('d-none');
            triggerBtn.innerHTML = '<i class="bi bi-grid-3x3-gap"></i> Seleccionar artículo';
            return;
        }

        preview.classList.remove('d-none');
        previewContent.innerHTML = cardMarkupFromOption(selected);
        triggerBtn.classList.add('d-none');
    }

    function calcularTotales() {
        let subtotal = 0;
        let total = 0;

        document.querySelectorAll('.producto-item').forEach(item => {
            const precioInput = item.querySelector('.precio-input');
            const cantidadInput = item.querySelector('.cantidad-input');

            const precio = parsearNumero(precioInput ? precioInput.value : '0');
            const cantidad = parseInt(cantidadInput ? cantidadInput.value : '1', 10) || 0;

            subtotal += precio;
            total += precio * cantidad;
        });

        document.getElementById('subtotal').textContent = '$' + formatearMiles(subtotal.toFixed(2));
        document.getElementById('total').textContent = '$' + formatearMiles(total.toFixed(2));
    }

    function configurarProductoItem(item) {
        const select = item.querySelector('.item-select');
        const precioInput = item.querySelector('.precio-input');
        const cantidadInput = item.querySelector('.cantidad-input');
        const btnEliminar = item.querySelector('.btn-eliminar-producto');
        item.querySelectorAll('.js-open-picker').forEach((pickerTrigger) => {
            pickerTrigger.addEventListener('click', function () {
                activePickerItem = item;
                renderPickerFor(item);
                itemPickerPanel && itemPickerPanel.classList.remove('d-none');
            });
        });

        if (precioInput) {
            precioInput.setAttribute('data-original-type', precioInput.type);
            precioInput.type = 'text';
            precioInput.inputMode = 'decimal';
            aplicarFormatoMiles(precioInput);
        }

        if (select) {
            select.addEventListener('change', function () {
                autocompletarPrecioItem(item, true);
            });
        }

        autocompletarPrecioItem(item, false);

        if (cantidadInput) {
            bloquearFlechas(cantidadInput);
            cantidadInput.addEventListener('input', calcularTotales);
        }

        if (btnEliminar) {
            btnEliminar.addEventListener('click', function () {
                const items = document.querySelectorAll('.producto-item');
                if (items.length > 1) {
                    if (activePickerItem === item) {
                        itemPickerPanel && itemPickerPanel.classList.add('d-none');
                        activePickerItem = null;
                    }
                    item.remove();
                    calcularTotales();
                } else {
                    alert('Debe tener al menos un producto en la compra');
                }
            });
        }
    }

    const btnAgregar = document.getElementById('btnAgregarProducto');
    if (btnAgregar) {
        btnAgregar.addEventListener('click', function () {
            if (!container) return;
            const primerItem = container.querySelector('.producto-item');
            if (!primerItem) return;

            const nuevoItem = primerItem.cloneNode(true);

            nuevoItem.querySelectorAll('input').forEach(input => {
                if (input.classList.contains('cantidad-input')) {
                    input.value = '1';
                } else {
                    input.value = '';
                }
                if (input.classList.contains('precio-input')) {
                    input.type = 'number';
                }
            });

            nuevoItem.querySelectorAll('select').forEach(select => {
                select.selectedIndex = 0;
            });

            const preview = nuevoItem.querySelector('.item-selected-preview');
            const previewContent = preview ? preview.querySelector('.item-selected-content') : null;
            const triggerBtn = nuevoItem.querySelector('.item-picker-trigger');
            if (preview) {
                preview.classList.add('d-none');
                if (previewContent) previewContent.innerHTML = '';
            }
            if (triggerBtn) {
                triggerBtn.classList.remove('d-none');
                triggerBtn.innerHTML = '<i class="bi bi-grid-3x3-gap"></i> Seleccionar artículo';
            }

            container.appendChild(nuevoItem);
            configurarProductoItem(nuevoItem);
        });
    }

    document.querySelectorAll('.producto-item').forEach(item => {
        configurarProductoItem(item);
    });

    if (container) {
        container.addEventListener('change', function (event) {
            const target = event.target;
            if (target && target.classList.contains('item-select')) {
                const item = target.closest('.producto-item');
                autocompletarPrecioItem(item, true);
            }
        });
    }

    const formCompra = document.getElementById('formCompra');
    if (formCompra) {
        formCompra.addEventListener('submit', function (e) {
            let productosValidos = 0;

            document.querySelectorAll('.precio-input').forEach((input) => {
                const valorLimpio = parsearNumero(input.value);
                input.type = 'number';
                input.value = valorLimpio > 0 ? valorLimpio : '';
                if (valorLimpio > 0) productosValidos++;
            });

            document.querySelectorAll('.cantidad-input').forEach((input) => {
                const cantidad = parseInt(input.value, 10) || 0;
                input.value = cantidad > 0 ? cantidad : '';
            });

            if (productosValidos === 0) {
                e.preventDefault();
                alert('Debe agregar al menos un producto con precio válido');
                return false;
            }
        });
    }

    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
    }
});