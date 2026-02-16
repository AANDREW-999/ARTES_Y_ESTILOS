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
            // Guardar el tipo original
            precioInput.setAttribute('data-original-type', precioInput.type);
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
                } else {
                    alert('Debe tener al menos un producto en la compra');
                }
            });
        }
    }

    // Agregar producto
    const btnAgregar = document.getElementById('btnAgregarProducto');
    if (btnAgregar) {
        btnAgregar.addEventListener('click', function () {
            const container = document.getElementById('productos-container');
            const primerItem = container.querySelector('.producto-item');
            const nuevoItem = primerItem.cloneNode(true);

            // Limpiar todos los inputs
            nuevoItem.querySelectorAll('input').forEach(input => {
                if (input.classList.contains('cantidad-input')) {
                    input.value = '1';
                } else {
                    input.value = '';
                }
                // Restablecer tipo de input si es precio
                if (input.classList.contains('precio-input')) {
                    input.type = 'number';
                }
            });

            container.appendChild(nuevoItem);
            configurarProductoItem(nuevoItem);
        });
    }

    // Descuento
    const descuentoInput = document.getElementById('descuento');
    if (descuentoInput) {
        descuentoInput.type = 'text';
        descuentoInput.inputMode = 'decimal';
        aplicarFormatoMiles(descuentoInput);
    }

    // Inicializar productos existentes
    document.querySelectorAll('.producto-item').forEach(item => {
        configurarProductoItem(item);
    });

    // Limpiar antes de enviar
    const formCompra = document.getElementById('formCompra');
    if (formCompra) {
        formCompra.addEventListener('submit', function (e) {
            console.log('📤 Enviando formulario de compra...');
            
            // Validar que haya al menos un producto con precio y cantidad
            let productosValidos = 0;
            
            // Restaurar inputs a tipo number y limpiar valores
            document.querySelectorAll('.precio-input').forEach((input, idx) => {
                const valorOriginal = input.value;
                const valorLimpio = parsearNumero(input.value);
                
                // Restaurar a tipo number
                input.type = 'number';
                input.value = valorLimpio > 0 ? valorLimpio : '';
                
                console.log(`   Precio[${idx}]: "${valorOriginal}" → ${input.value}`);
                
                if (valorLimpio > 0) {
                    productosValidos++;
                }
            });
            
            // Limpiar descuento
            if (descuentoInput && descuentoInput.value) {
                const descuentoOriginal = descuentoInput.value;
                const descuentoLimpio = parsearNumero(descuentoInput.value);
                descuentoInput.type = 'number';
                descuentoInput.value = descuentoLimpio;
                console.log(`   Descuento: "${descuentoOriginal}" → ${descuentoInput.value}`);
            }
            
            // Validar cantidades
            document.querySelectorAll('.cantidad-input').forEach((input, idx) => {
                const cantidad = parseInt(input.value) || 0;
                console.log(`   Cantidad[${idx}]: ${cantidad}`);
            });
            
            if (productosValidos === 0) {
                e.preventDefault();
                alert('Debe agregar al menos un producto con precio válido');
                return false;
            }
            
            console.log(` Validación OK - ${productosValidos} producto(s) válido(s)`);
        });
    }

    // Toggle sidebar
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
    }

});