document.addEventListener("DOMContentLoaded", function () {
    const addItemBtn = document.getElementById("addItem");
    const itemsContainer = document.getElementById("itemsContainer");
    const totalSpan = document.getElementById("totalVenta");
    const subtotalSpan = document.getElementById("subtotalVenta");
    const formVenta = document.getElementById("formVenta");
    const manoObraInput = document.getElementById("manoObra");
    const domicilioCheckbox = document.getElementById("id_con_domicilio");
    const camposDomicilio = document.getElementById("campos_domicilio");
    const direccionInput = document.getElementById("id_direccion");
    const nombreDomiciliarioInput = document.getElementById("id_nombre_domiciliario");
    const telefonoDomiciliarioInput = document.getElementById("id_telefono_domiciliario");
    const envioInput = document.getElementById("id_precio_envio");

    if (!addItemBtn || !itemsContainer) {
        return;
    }

    addItemBtn.addEventListener("click", agregarItem);
    manoObraInput && manoObraInput.addEventListener("input", calcularTotal);
    envioInput && envioInput.addEventListener("input", calcularTotal);

    if (manoObraInput) {
        manoObraInput.addEventListener("focus", () => {
            const numero = parsearMonedaInput(manoObraInput.value);
            manoObraInput.value = numero ? numero.toFixed(2) : "";
        });

        manoObraInput.addEventListener("blur", () => {
            const numero = parsearMonedaInput(manoObraInput.value);
            manoObraInput.value = numero ? formatearMonedaInput(numero) : "0,00";
            calcularTotal();
        });

        const inicial = parsearMonedaInput(manoObraInput.value);
        manoObraInput.value = formatearMonedaInput(inicial);
    }

    if (formVenta) {
        formVenta.addEventListener("submit", () => {
            if (!manoObraInput) return;
            const numero = parsearMonedaInput(manoObraInput.value);
            manoObraInput.value = numero.toFixed(2);
        });
    }

    if (domicilioCheckbox) {
        domicilioCheckbox.addEventListener("change", () => {
            if (camposDomicilio) {
                camposDomicilio.classList.toggle("d-none", !domicilioCheckbox.checked);
            }
            actualizarValidacionDomicilio();
            calcularTotal();
        });
    }

    if (domicilioCheckbox && camposDomicilio) {
        camposDomicilio.classList.toggle("d-none", !domicilioCheckbox.checked);
    }

    actualizarValidacionDomicilio();

    itemsContainer.querySelectorAll(".item-venta").forEach(configurarItem);
    calcularTotal();

    function parsearPrecioData(valor) {
        if (!valor) return 0;
        const str = String(valor).trim();
        if (!str) return 0;

        // Soporta 10000.50 y 10.000,50
        if (str.includes(',')) {
            return parseFloat(str.replace(/\./g, '').replace(',', '.')) || 0;
        }
        return parseFloat(str) || 0;
    }

    function parsearMonedaInput(valor) {
        if (!valor) return 0;
        const str = String(valor).trim();
        if (!str) return 0;

        if (str.includes(",")) {
            return parseFloat(str.replace(/\./g, "").replace(",", ".")) || 0;
        }
        return parseFloat(str) || 0;
    }

    function formatearMonedaInput(numero) {
        return Number(numero || 0).toLocaleString("es-CO", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    function agregarItem() {
        const primerItem = itemsContainer.querySelector(".item-venta");
        if (!primerItem) {
            return;
        }

        const nuevoItem = primerItem.cloneNode(true);

        const select = nuevoItem.querySelector(".item-select");
        const precioInput = nuevoItem.querySelector(".precio");
        const cantidadInput = nuevoItem.querySelector(".cantidad");
        const subtotal = nuevoItem.querySelector(".subtotal");

        if (select) {
            select.selectedIndex = 0;
        }
        if (precioInput) {
            precioInput.value = "0";
        }
        if (cantidadInput) {
            cantidadInput.value = "1";
        }
        if (subtotal) {
            subtotal.innerText = "$0.00";
        }

        itemsContainer.appendChild(nuevoItem);
        configurarItem(nuevoItem);
        calcularTotal();
    }

    function configurarItem(itemEl) {
        const select = itemEl.querySelector(".item-select");
        const precioInput = itemEl.querySelector(".precio");
        const cantidadInput = itemEl.querySelector(".cantidad");
        const removeBtn = itemEl.querySelector(".eliminar");

        if (select && precioInput) {
            const autocompletarPrecio = (forzar) => {
                const selectedOption = select.options[select.selectedIndex];
                const precio = selectedOption ? selectedOption.getAttribute("data-precio") : null;
                const precioActual = parseFloat(precioInput.value) || 0;
                const precioNum = parsearPrecioData(precio);

                if (precioNum > 0 && (forzar || !precioActual || precioActual <= 0)) {
                    precioInput.value = precioNum.toFixed(2);
                } else if (forzar && !precioNum) {
                    precioInput.value = "0";
                }
                calcularTotal();
            };

            select.addEventListener("change", () => autocompletarPrecio(true));
            autocompletarPrecio(false);
        }

        precioInput && precioInput.addEventListener("input", calcularTotal);
        cantidadInput && cantidadInput.addEventListener("input", calcularTotal);

        if (removeBtn) {
            removeBtn.addEventListener("click", () => {
                const totalItems = itemsContainer.querySelectorAll(".item-venta").length;
                if (totalItems > 1) {
                    itemEl.remove();
                    calcularTotal();
                }
            });
        }
    }

    function calcularTotal() {
        let subtotal = 0;

        itemsContainer.querySelectorAll(".item-venta").forEach((itemEl) => {
            const cantidad = parseFloat(itemEl.querySelector(".cantidad")?.value) || 0;
            const precio = parseFloat(itemEl.querySelector(".precio")?.value) || 0;
            const sub = cantidad * precio;

            const subtotalEl = itemEl.querySelector(".subtotal");
            if (subtotalEl) {
                subtotalEl.innerText = fmt(sub);
            }

            subtotal += sub;
        });

        subtotal += parsearMonedaInput(manoObraInput?.value);

        if (domicilioCheckbox?.checked && envioInput) {
            subtotal += parseFloat(envioInput.value) || 0;
        }

        const total = subtotal;

        if (subtotalSpan) subtotalSpan.innerText = fmt(subtotal);
        if (totalSpan) totalSpan.innerText = fmt(total);

        const hiddenTotal = document.getElementById("hiddenTotal");
        if (hiddenTotal) {
            hiddenTotal.value = total.toFixed(2);
        }
    }

    function actualizarValidacionDomicilio() {
        const conDomicilio = Boolean(domicilioCheckbox?.checked);
        [direccionInput, nombreDomiciliarioInput, telefonoDomiciliarioInput, envioInput].forEach((input) => {
            if (!input) return;
            input.required = conDomicilio;
        });
    }

    function fmt(n) {
        return "$" + n.toLocaleString("es-CO", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }
});
