document.addEventListener("DOMContentLoaded", function () {
    const addItemBtn = document.getElementById("addItem");
    const itemsContainer = document.getElementById("itemsContainer");
    const totalSpan = document.getElementById("totalVenta");
    const subtotalSpan = document.getElementById("subtotalVenta");
    const ivaSpan = document.getElementById("ivaVenta");
    const manoObraInput = document.getElementById("manoObra");
    const domicilioCheckbox = document.getElementById("id_con_domicilio");
    const camposDomicilio = document.getElementById("campos_domicilio");
    const ivaSelect = document.getElementById("ivaSelect");
    const envioInput = document.getElementById("id_precio_envio");

    if (!addItemBtn || !itemsContainer) {
        return;
    }

    addItemBtn.addEventListener("click", agregarItem);
    manoObraInput && manoObraInput.addEventListener("input", calcularTotal);
    ivaSelect && ivaSelect.addEventListener("change", calcularTotal);
    envioInput && envioInput.addEventListener("input", calcularTotal);

    if (domicilioCheckbox) {
        domicilioCheckbox.addEventListener("change", () => {
            if (camposDomicilio) {
                camposDomicilio.classList.toggle("d-none", !domicilioCheckbox.checked);
            }
            calcularTotal();
        });
    }

    if (domicilioCheckbox && camposDomicilio) {
        camposDomicilio.classList.toggle("d-none", !domicilioCheckbox.checked);
    }

    itemsContainer.querySelectorAll(".item-venta").forEach(configurarItem);
    calcularTotal();

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
            select.addEventListener("change", () => {
                const selectedOption = select.options[select.selectedIndex];
                const precio = selectedOption ? selectedOption.getAttribute("data-precio") : null;
                if (precio) {
                    precioInput.value = precio;
                }
                calcularTotal();
            });
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

        subtotal += parseFloat(manoObraInput?.value) || 0;

        if (domicilioCheckbox?.checked && envioInput) {
            subtotal += parseFloat(envioInput.value) || 0;
        }

        const ivaPct = parseFloat(ivaSelect?.value) || 0;
        const ivaMonto = subtotal * (ivaPct / 100);
        const total = subtotal + ivaMonto;

        if (subtotalSpan) subtotalSpan.innerText = fmt(subtotal);
        if (ivaSpan) ivaSpan.innerText = `${fmt(ivaMonto)} (${ivaPct}%)`;
        if (totalSpan) totalSpan.innerText = fmt(total);

        const hiddenTotal = document.getElementById("hiddenTotal");
        if (hiddenTotal) {
            hiddenTotal.value = total.toFixed(2);
        }
    }

    function fmt(n) {
        return "$" + n.toLocaleString("es-CO", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }
});
