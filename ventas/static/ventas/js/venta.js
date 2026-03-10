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
    const itemPickerPanel = document.getElementById("itemPickerPanel");
    const itemPickerGrid = document.getElementById("itemPickerGrid");

    let activePickerItem = null;

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
        if (str.includes(",")) {
            return parseFloat(str.replace(/\./g, "").replace(",", ".")) || 0;
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

    function getStockClass(stock) {
        const s = parseInt(stock, 10) || 0;
        if (s <= 5) return "stock-low text-danger";
        if (s <= 15) return "stock-medium text-warning";
        return "stock-high text-success";
    }

    function escapeHtml(str) {
        return String(str || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function cardMarkupFromOption(option) {
        const nombre = (option.textContent || "").replace(/\(Stock:.*\)/i, "").trim() || "Item";
        const tipo = option.getAttribute("data-tipo") || "Item";
        const stock = option.getAttribute("data-stock") || "0";
        const imagen = option.getAttribute("data-imagen") || "";
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

    function renderPickerFor(itemEl) {
        if (!itemPickerPanel || !itemPickerGrid) return;
        const select = itemEl.querySelector(".item-select");
        if (!select) return;

        itemPickerGrid.innerHTML = "";
        Array.from(select.options).forEach((option) => {
            if (!option.value) return;

            const card = document.createElement("button");
            card.type = "button";
            card.className = "item-picker-option";
            card.innerHTML = cardMarkupFromOption(option);
            card.addEventListener("click", () => {
                select.value = option.value;
                select.dispatchEvent(new Event("change", { bubbles: true }));
                itemPickerPanel.classList.add("d-none");
                activePickerItem = null;
            });
            itemPickerGrid.appendChild(card);
        });
    }

    function actualizarPreview(itemEl) {
        const select = itemEl.querySelector(".item-select");
        const preview = itemEl.querySelector(".item-selected-preview");
        const previewContent = preview ? preview.querySelector(".item-selected-content") : null;
        const triggerBtn = itemEl.querySelector(".item-picker-trigger");
        if (!select || !preview || !previewContent || !triggerBtn) return;

        const selected = select.options[select.selectedIndex];
        if (!selected || !selected.value) {
            preview.classList.add("d-none");
            previewContent.innerHTML = "";
            triggerBtn.classList.remove("d-none");
            triggerBtn.innerHTML = '<i class="bi bi-grid-3x3-gap"></i> Seleccionar ítem';
            return;
        }

        preview.classList.remove("d-none");
        previewContent.innerHTML = cardMarkupFromOption(selected);
        triggerBtn.classList.add("d-none");
    }

    function agregarItem() {
        const primerItem = itemsContainer.querySelector(".item-venta");
        if (!primerItem) return;

        const nuevoItem = primerItem.cloneNode(true);
        const select = nuevoItem.querySelector(".item-select");
        const precioInput = nuevoItem.querySelector(".precio");
        const cantidadInput = nuevoItem.querySelector(".cantidad");
        const subtotal = nuevoItem.querySelector(".subtotal");
        const preview = nuevoItem.querySelector(".item-selected-preview");
        const previewContent = preview ? preview.querySelector(".item-selected-content") : null;
        const triggerBtn = nuevoItem.querySelector(".item-picker-trigger");

        if (select) select.selectedIndex = 0;
        if (precioInput) precioInput.value = "0";
        if (cantidadInput) cantidadInput.value = "1";
        if (subtotal) subtotal.innerText = "$0.00";
        if (preview) {
            preview.classList.add("d-none");
            if (previewContent) previewContent.innerHTML = "";
        }
        if (triggerBtn) {
            triggerBtn.classList.remove("d-none");
            triggerBtn.innerHTML = '<i class="bi bi-grid-3x3-gap"></i> Seleccionar ítem';
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
        itemEl.querySelectorAll(".js-open-picker").forEach((pickerTrigger) => {
            pickerTrigger.addEventListener("click", () => {
                activePickerItem = itemEl;
                renderPickerFor(itemEl);
                itemPickerPanel && itemPickerPanel.classList.remove("d-none");
            });
        });

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

                actualizarPreview(itemEl);
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
                    if (activePickerItem === itemEl) {
                        itemPickerPanel && itemPickerPanel.classList.add("d-none");
                        activePickerItem = null;
                    }
                    itemEl.remove();
                    calcularTotal();
                }
            });
        }
    }

    function calcularTotal() {
        let subtotal = 0;
        let totalItems = 0;

        itemsContainer.querySelectorAll(".item-venta").forEach((itemEl) => {
            const cantidad = parseFloat(itemEl.querySelector(".cantidad")?.value) || 0;
            const precio = parseFloat(itemEl.querySelector(".precio")?.value) || 0;
            const sub = cantidad * precio;

            subtotal += precio;
            totalItems += sub;

            const subtotalEl = itemEl.querySelector(".subtotal");
            if (subtotalEl) subtotalEl.innerText = fmt(sub);
        });

        let total = totalItems;
        total += parsearMonedaInput(manoObraInput?.value);
        if (domicilioCheckbox?.checked && envioInput) {
            total += parseFloat(envioInput.value) || 0;
        }

        if (subtotalSpan) subtotalSpan.innerText = fmt(subtotal);
        if (totalSpan) totalSpan.innerText = fmt(total);

        const hiddenTotal = document.getElementById("hiddenTotal");
        if (hiddenTotal) hiddenTotal.value = total.toFixed(2);
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
