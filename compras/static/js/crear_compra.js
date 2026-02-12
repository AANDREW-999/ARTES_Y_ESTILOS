document.addEventListener('DOMContentLoaded', function () {

    // Fecha automática
    const fechaInput = document.getElementById('fecha_emision');
    if (fechaInput) {
        const hoy = new Date();
        const año = hoy.getFullYear();
        const mes = String(hoy.getMonth() + 1).padStart(2, '0');
        const dia = String(hoy.getDate()).padStart(2, '0');
        fechaInput.value = `${año}-${mes}-${dia}`;
    }

    // Utilidades de formato
    function limpiarNumero(valor) {
        return valor.replace(/[^\d.]/g, '');
    }

    function formatearMiles(valor) {
        const partes = String(valor).split('.');
        const entero = partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return partes.length > 1 ? `${entero},${partes[1]}` : entero;
    }

    function parsearNumero(valor) {
        return parseFloat(valor.replace(/\./g, '').replace(',', '.')) || 0;
    }

    // Bloquear flechas en inputs numéricos
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

    // Aplicar formato de miles
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

    // Calcular totales
    function calcularTotales() {
        let subtotal = 0;

        document.querySelectorAll('.producto-item').forEach(item => {
            const precioInput = item.querySelector('.precio-input');
            const cantidadInput = item.querySelector('.cantidad-input');

            const precio = parsearNumero(precioInput ? precioInput.value : '0');
            const cantidad = parseInt(cantidadInput ? cantidadInput.value : '1') || 0;

            subtotal += precio * cantidad;
        });

        const descuentoInput = document.getElementById('descuento');
        const descuento = parsearNumero(descuentoInput ? descuentoInput.value : '0');
        const totalDescuento = subtotal * (descuento / 100);
        const total = subtotal - totalDescuento;

        document.getElementById('subtotal').textContent = '$' + formatearMiles(subtotal.toFixed(2));
        document.getElementById('total').textContent = '$' + formatearMiles(total.toFixed(2));
    }

    // Configurar producto item
    function configurarProductoItem(item) {
        const precioInput = item.querySelector('.precio-input');
        const cantidadInput = item.querySelector('.cantidad-input');
        const btnEliminar = item.querySelector('.btn-eliminar-producto');

        if (precioInput) {
            precioInput.type = 'text';
            precioInput.inputMode = 'decimal';
            aplicarFormatoMiles(precioInput);
        }

        if (cantidadInput) {
            bloquearFlechas(cantidadInput);
            cantidadInput.addEventListener('input', calcularTotales);
        }

        if (btnEliminar) {
            btnEliminar.addEventListener('click', function () {
                const items = document.querySelectorAll('.producto-item');
                if (items.length > 1) {
                    item.remove();
                    calcularTotales();
                }
            });
        }
    }

    // Agregar producto
    document.getElementById('btnAgregarProducto')?.addEventListener('click', function () {
        const container = document.getElementById('productos-container');
        const primerItem = container.querySelector('.producto-item');
        const nuevoItem = primerItem.cloneNode(true);

        nuevoItem.querySelectorAll('input').forEach(input => {
            input.value = input.type === 'number' ? (input.name.includes('cantidad') ? '1' : '') : '';
        });

        container.appendChild(nuevoItem);
        configurarProductoItem(nuevoItem);
    });

    // Descuento
    const descuentoInput = document.getElementById('descuento');
    if (descuentoInput) {
        descuentoInput.type = 'text';
        descuentoInput.inputMode = 'decimal';
        aplicarFormatoMiles(descuentoInput);
    }

    // Inicializar productos
    document.querySelectorAll('.producto-item').forEach(item => {
        configurarProductoItem(item);
    });

    // Limpiar antes de enviar
    document.getElementById('formCompra')?.addEventListener('submit', function () {
        document.querySelectorAll('.precio-input').forEach(input => {
            input.value = parsearNumero(input.value);
        });
        if (descuentoInput) {
            descuentoInput.value = parsearNumero(descuentoInput.value);
        }
    });

    // Toggle sidebar - CORRECCIÓN AQUÍ
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
    }

});