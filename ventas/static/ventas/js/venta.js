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
    const tipoVentaInput = document.getElementById("id_tipo_venta");
    const formaPagoInput = document.getElementById("id_forma_pago");
    const fechaInput = document.getElementById("id_fecha");
    const clienteInput = document.getElementById("id_cliente");

    let activePickerItem = null;

    if (!addItemBtn || !itemsContainer) {
        return;
    }

    function mostrarAlertaAdmin(tipo, mensaje) {
        if (window._dashboard && typeof window._dashboard.showAdminNotification === "function") {
            window._dashboard.showAdminNotification(tipo || "warning", mensaje || "Ocurrio un problema.");
            return;
        }

        if (typeof window.bootstrap !== "undefined") {
            const toastId = (tipo === "error") ? "errorToast" : "warningToast";
            const msgId = (tipo === "error") ? "errorToastMessage" : "warningToastMessage";
            const toastEl = document.getElementById(toastId);
            const msgEl = document.getElementById(msgId);
            if (toastEl && msgEl) {
                msgEl.textContent = mensaje;
                window.bootstrap.Toast.getOrCreateInstance(toastEl).show();
                return;
            }
        }

        console.warn("[venta] " + mensaje);
    }

    function setFieldValidation(input, isValid, message) {
        if (!input) return;
        const wrapper = input.closest(".field-wrapper");
        const invalid = wrapper ? wrapper.querySelector(".invalid-feedback") : null;
        const valid = wrapper ? wrapper.querySelector(".valid-feedback") : null;

        input.classList.remove("is-valid", "is-invalid");
        if (invalid) {
            invalid.style.display = "none";
            invalid.textContent = "";
        }
        if (valid) {
            valid.style.display = "none";
            valid.textContent = "";
        }

        if (isValid) {
            input.classList.add("is-valid");
            if (valid && message) {
                valid.textContent = message;
                valid.style.display = "block";
            }
        } else {
            input.classList.add("is-invalid");
            if (invalid) {
                invalid.textContent = message || "Campo invalido.";
                invalid.style.display = "block";
            }
        }
    }

    function validarFechaNoFutura(input) {
        if (!input) return true;
        const valor = String(input.value || "").trim();
        if (!valor) {
            setFieldValidation(input, false, "La fecha es obligatoria.");
            return false;
        }

        const fecha = new Date(valor);
        if (Number.isNaN(fecha.getTime())) {
            setFieldValidation(input, false, "Fecha invalida.");
            return false;
        }

        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);
        fecha.setHours(0, 0, 0, 0);
        if (fecha > hoy) {
            setFieldValidation(input, false, "La fecha no puede ser futura.");
            return false;
        }

        const limite = new Date("1900-01-01");
        limite.setHours(0, 0, 0, 0);
        if (fecha < limite) {
            setFieldValidation(input, false, "La fecha es demasiado antigua.");
            return false;
        }

        setFieldValidation(input, true, "Fecha válida");
        return true;
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

    if (tipoVentaInput) {
        tipoVentaInput.addEventListener("change", function () {
            const ok = String(this.value || "").trim() !== "";
            setFieldValidation(this, ok, ok ? "Tipo de venta válido" : "Este campo es obligatorio.");
        });
    }

    if (formaPagoInput) {
        formaPagoInput.addEventListener("change", function () {
            const ok = String(this.value || "").trim() !== "";
            setFieldValidation(this, ok, ok ? "Forma de pago válida" : "Este campo es obligatorio.");
        });
    }

    if (clienteInput) {
        clienteInput.addEventListener("change", function () {
            const ok = String(this.value || "").trim() !== "";
            setFieldValidation(this, ok, ok ? "Cliente válido" : "Este campo es obligatorio.");
        });
    }

    if (fechaInput) {
        fechaInput.addEventListener("change", function () {
            validarFechaNoFutura(this);
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

    direccionInput && direccionInput.addEventListener("input", () => {
        if (!domicilioCheckbox?.checked) return;
        const ok = String(direccionInput.value || "").trim() !== "";
        setFieldValidation(direccionInput, ok, ok ? "Dirección válida" : "La dirección es obligatoria cuando la venta es con domicilio.");
    });

    nombreDomiciliarioInput && nombreDomiciliarioInput.addEventListener("input", () => {
        if (!domicilioCheckbox?.checked) return;
        const ok = String(nombreDomiciliarioInput.value || "").trim() !== "";
        setFieldValidation(nombreDomiciliarioInput, ok, ok ? "Nombre válido" : "El nombre del domiciliario es obligatorio.");
    });

    telefonoDomiciliarioInput && telefonoDomiciliarioInput.addEventListener("input", () => {
        if (!domicilioCheckbox?.checked) return;
        const valor = String(telefonoDomiciliarioInput.value || "").trim();
        const limpio = valor.replace(/\s|-/g, "");
        const ok = /^\+?\d{7,15}$/.test(limpio);
        setFieldValidation(
            telefonoDomiciliarioInput,
            ok,
            ok ? "Teléfono válido" : "Ingresa un teléfono válido (solo números, 7 a 15 dígitos)."
        );
    });

    envioInput && envioInput.addEventListener("input", () => {
        if (!domicilioCheckbox?.checked) return;
        const num = parseFloat(envioInput.value);
        const ok = Number.isFinite(num) && num >= 0;
        setFieldValidation(envioInput, ok, ok ? "Costo de envío válido" : "El costo de envío es obligatorio cuando hay domicilio.");
    });

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
        if (s <= 10) return "stock-low text-danger";
        if (s <= 30) return "stock-medium text-warning";
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

        const validarCantidadContraStock = () => {
            if (!cantidadInput || !select) return true;

            const cantidad = parseInt(cantidadInput.value, 10) || 0;
            if (cantidad <= 0) {
                setFieldValidation(cantidadInput, false, "La cantidad debe ser mayor que 0.");
                return false;
            }

            const selectedOption = select.options[select.selectedIndex];
            const stock = parseInt(selectedOption?.getAttribute("data-stock"), 10);
            if (Number.isFinite(stock) && cantidad > stock) {
                setFieldValidation(cantidadInput, false, "La cantidad no debe ser mayor al stock disponible.");
                return false;
            }

            setFieldValidation(cantidadInput, true, "");
            return true;
        };

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
                const itemOk = String(select.value || "").trim() !== "";
                setFieldValidation(select, itemOk, itemOk ? "" : "Debes seleccionar un ítem.");

                const precioVal = parseFloat(precioInput.value) || 0;
                setFieldValidation(precioInput, precioVal > 0, precioVal > 0 ? "" : "El precio debe ser mayor que 0.");
                validarCantidadContraStock();
                calcularTotal();
            };

            select.addEventListener("change", () => autocompletarPrecio(true));
            autocompletarPrecio(false);
        }

        precioInput && precioInput.addEventListener("input", calcularTotal);
        cantidadInput && cantidadInput.addEventListener("input", calcularTotal);

        if (cantidadInput) {
            cantidadInput.addEventListener("input", validarCantidadContraStock);
        }

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

    function validarCamposDomicilio() {
        if (!domicilioCheckbox?.checked) return { ok: true, firstInvalid: null };

        let ok = true;
        let firstInvalid = null;

        const direccionOk = String(direccionInput?.value || "").trim() !== "";
        setFieldValidation(direccionInput, direccionOk, direccionOk ? "Dirección válida" : "La dirección es obligatoria cuando la venta es con domicilio.");
        if (!direccionOk) {
            ok = false;
            if (!firstInvalid) firstInvalid = direccionInput;
        }

        const nombreOk = String(nombreDomiciliarioInput?.value || "").trim() !== "";
        setFieldValidation(nombreDomiciliarioInput, nombreOk, nombreOk ? "Nombre válido" : "El nombre del domiciliario es obligatorio.");
        if (!nombreOk) {
            ok = false;
            if (!firstInvalid) firstInvalid = nombreDomiciliarioInput;
        }

        const telefono = String(telefonoDomiciliarioInput?.value || "").trim();
        const telefonoLimpio = telefono.replace(/\s|-/g, "");
        const telefonoOk = /^\+?\d{7,15}$/.test(telefonoLimpio);
        setFieldValidation(
            telefonoDomiciliarioInput,
            telefonoOk,
            telefonoOk ? "Teléfono válido" : "Ingresa un teléfono válido (solo números, 7 a 15 dígitos)."
        );
        if (!telefonoOk) {
            ok = false;
            if (!firstInvalid) firstInvalid = telefonoDomiciliarioInput;
        }

        const envio = parseFloat(envioInput?.value);
        const envioOk = Number.isFinite(envio) && envio >= 0;
        setFieldValidation(envioInput, envioOk, envioOk ? "Costo de envío válido" : "El costo de envío es obligatorio cuando hay domicilio.");
        if (!envioOk) {
            ok = false;
            if (!firstInvalid) firstInvalid = envioInput;
        }

        return { ok, firstInvalid };
    }

    if (formVenta) {
        formVenta.addEventListener("submit", (e) => {
            let formOk = true;
            let firstInvalid = null;
            let productosValidos = 0;

            const numero = parsearMonedaInput(manoObraInput?.value);
            if (manoObraInput) {
                manoObraInput.value = Number.isFinite(numero) ? numero.toFixed(2) : "0.00";
            }

            const tipoOk = String(tipoVentaInput?.value || "").trim() !== "";
            setFieldValidation(tipoVentaInput, tipoOk, tipoOk ? "Tipo de venta válido" : "Este campo es obligatorio.");
            if (!tipoOk) {
                formOk = false;
                if (!firstInvalid) firstInvalid = tipoVentaInput;
            }

            const pagoOk = String(formaPagoInput?.value || "").trim() !== "";
            setFieldValidation(formaPagoInput, pagoOk, pagoOk ? "Forma de pago válida" : "Este campo es obligatorio.");
            if (!pagoOk) {
                formOk = false;
                if (!firstInvalid) firstInvalid = formaPagoInput;
            }

            const clienteOk = String(clienteInput?.value || "").trim() !== "";
            setFieldValidation(clienteInput, clienteOk, clienteOk ? "Cliente válido" : "Este campo es obligatorio.");
            if (!clienteOk) {
                formOk = false;
                if (!firstInvalid) firstInvalid = clienteInput;
            }

            if (!validarFechaNoFutura(fechaInput)) {
                formOk = false;
                if (!firstInvalid) firstInvalid = fechaInput;
            }

            itemsContainer.querySelectorAll(".item-venta").forEach((itemEl) => {
                const select = itemEl.querySelector(".item-select");
                const precioInput = itemEl.querySelector(".precio");
                const cantidadInput = itemEl.querySelector(".cantidad");

                const itemOk = String(select?.value || "").trim() !== "";
                setFieldValidation(select, itemOk, itemOk ? "" : "Debes seleccionar un ítem.");
                if (!itemOk) {
                    formOk = false;
                    if (!firstInvalid) firstInvalid = select;
                }

                const precio = parseFloat(precioInput?.value) || 0;
                const precioOk = precio > 0;
                setFieldValidation(precioInput, precioOk, precioOk ? "" : "El precio debe ser mayor que 0.");
                if (!precioOk) {
                    formOk = false;
                    if (!firstInvalid) firstInvalid = precioInput;
                } else {
                    productosValidos++;
                }

                const cantidad = parseInt(cantidadInput?.value, 10) || 0;
                const selectedOption = select?.options?.[select.selectedIndex];
                const stock = parseInt(selectedOption?.getAttribute("data-stock"), 10);
                let cantidadOk = cantidad > 0;
                let mensajeCantidad = "";

                if (!cantidadOk) {
                    mensajeCantidad = "La cantidad debe ser mayor que 0.";
                } else if (Number.isFinite(stock) && cantidad > stock) {
                    cantidadOk = false;
                    mensajeCantidad = "La cantidad no debe ser mayor al stock disponible.";
                }

                setFieldValidation(cantidadInput, cantidadOk, cantidadOk ? "" : mensajeCantidad);
                if (!cantidadOk) {
                    formOk = false;
                    if (!firstInvalid) firstInvalid = cantidadInput;
                }
            });

            const domicilioRes = validarCamposDomicilio();
            if (!domicilioRes.ok) {
                formOk = false;
                if (!firstInvalid) firstInvalid = domicilioRes.firstInvalid;
            }

            if (productosValidos === 0) {
                formOk = false;
                mostrarAlertaAdmin("warning", "Debes agregar al menos un item a la venta.");
            }

            if (!formOk) {
                e.preventDefault();
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
                    setTimeout(() => firstInvalid.focus(), 250);
                }
                if (productosValidos > 0) {
                    mostrarAlertaAdmin("warning", "Por favor, corrija los errores del formulario.");
                }
                return false;
            }
        });
    }

    function fmt(n) {
        return "$" + n.toLocaleString("es-CO", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }
});
