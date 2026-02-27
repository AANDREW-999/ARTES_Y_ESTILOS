document.addEventListener("DOMContentLoaded", function () {

    // ── Elementos del DOM ─────────────────────────────────────────────────
    const addItemBtn        = document.getElementById("addItem");
    const tableBody         = document.querySelector("#itemsTable tbody");
    const totalSpan         = document.getElementById("totalVenta");
    const subtotalSpan      = document.getElementById("subtotalVenta");
    const ivaSpan           = document.getElementById("ivaVenta");
    const manoObraInput     = document.getElementById("manoObra");
    const domicilioCheckbox = document.getElementById("id_con_domicilio");
    const camposDomicilio   = document.getElementById("campos_domicilio");
    const ivaSelect         = document.getElementById("ivaSelect");
    const envioInput        = document.getElementById("id_precio_envio");

    if (!addItemBtn || !tableBody) {
        console.error("venta.js: no se encontró #addItem o #itemsTable tbody");
        return;
    }

    // ── URL del endpoint (inyectada desde Django en el HTML) ──────────────
    const AJAX_URL = (typeof BUSCAR_ARREGLO_URL !== "undefined")
        ? BUSCAR_ARREGLO_URL
        : "/ventas/ajax/arreglos/";

    // ── Eventos globales ──────────────────────────────────────────────────
    addItemBtn.addEventListener("click", agregarFila);
    manoObraInput && manoObraInput.addEventListener("input", calcularTotal);
    ivaSelect     && ivaSelect.addEventListener("change", calcularTotal);
    envioInput    && envioInput.addEventListener("input", calcularTotal);

    if (domicilioCheckbox) {
        domicilioCheckbox.addEventListener("change", () => {
            camposDomicilio.style.display = domicilioCheckbox.checked ? "flex" : "none";
            calcularTotal();
        });
    }

    // Primera fila automática
    agregarFila();

    // ── Agregar fila ──────────────────────────────────────────────────────
    function agregarFila() {
        const emptyRow = document.getElementById("emptyRow");
        if (emptyRow) emptyRow.remove();

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="position-relative" style="min-width:260px;">
                <input type="text"   class="form-control buscar-arreglo" placeholder="Escribe para buscar arreglo...">
                <input type="hidden" name="arreglo_id[]" class="arreglo-id">
                <div class="autocomplete-box list-group position-absolute w-100" style="z-index:1055;top:100%;left:0;display:none;"></div>
            </td>
            <td style="width:110px;">
                <input type="number" class="form-control cantidad" name="cantidad[]" value="1" min="1">
            </td>
            <td style="width:150px;">
                <input type="number" class="form-control precio" name="precio[]" value="0" min="0" step="0.01">
            </td>
            <td class="subtotal text-end fw-semibold align-middle" style="width:140px;">$0.00</td>
            <td class="text-center align-middle" style="width:60px;">
                <button type="button" class="btn btn-danger btn-sm eliminar" title="Eliminar fila">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;

        tableBody.appendChild(tr);

        tr.querySelector(".eliminar").addEventListener("click", () => {
            tr.remove();
            calcularTotal();
            mostrarFilaVacia();
        });

        tr.querySelectorAll(".cantidad, .precio").forEach(el =>
            el.addEventListener("input", calcularTotal)
        );

        activarAutocomplete(tr);
        calcularTotal();
    }

    // ── Autocomplete ──────────────────────────────────────────────────────
    function activarAutocomplete(row) {
        const input      = row.querySelector(".buscar-arreglo");
        const hiddenId   = row.querySelector(".arreglo-id");
        const priceInput = row.querySelector(".precio");
        const box        = row.querySelector(".autocomplete-box");

        let debounceTimer = null;

        input.addEventListener("input", function () {
            clearTimeout(debounceTimer);
            const query = this.value.trim();

            if (query.length < 2) {
                cerrarBox(box);
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`${AJAX_URL}?q=${encodeURIComponent(query)}`)
                    .then(res => {
                        if (!res.ok) throw new Error(`HTTP ${res.status} en ${AJAX_URL}`);
                        return res.json();
                    })
                    .then(data => {
                        // Mostrar error de Django si viene en la respuesta
                        if (data.error) {
                            console.error("Error del servidor:", data.error);
                            mostrarEnBox(box, `<div class="list-group-item text-danger small py-2">
                                Error del servidor: ${data.error}
                            </div>`);
                            return;
                        }

                        // Soporte para clave 'arreglos' (nuevo) y 'arreglo' (legado)
                        const lista = Array.isArray(data.arreglos) ? data.arreglos
                                    : Array.isArray(data.arreglo)  ? data.arreglo
                                    : [];

                        if (lista.length === 0) {
                            mostrarEnBox(box, `<div class="list-group-item text-muted small py-2">
                                Sin resultados para <strong>${query}</strong>
                            </div>`);
                            return;
                        }

                        box.innerHTML = "";
                        lista.forEach(item => {
                            const a = document.createElement("a");
                            a.className = "list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2 px-3";
                            a.innerHTML = `
                                <span class="small">${item.nombre_flor}</span>
                                <span class="badge bg-success rounded-pill ms-2">$${parseFloat(item.precio).toLocaleString("es-CO")}</span>
                            `;
                            a.style.cursor = "pointer";
                            // mousedown para no perder el foco antes del click
                            a.addEventListener("mousedown", (e) => {
                                e.preventDefault();
                                input.value      = item.nombre_flor;
                                hiddenId.value   = item.id;
                                priceInput.value = item.precio;
                                cerrarBox(box);
                                calcularTotal();
                            });
                            box.appendChild(a);
                        });
                        box.style.display = "block";
                    })
                    .catch(err => {
                        console.error("Fetch arreglos falló:", err);
                        mostrarEnBox(box, `<div class="list-group-item text-danger small py-2">
                            No se pudo conectar. Revisa la consola (F12).
                        </div>`);
                    });
            }, 300); // debounce 300ms
        });

        // Cerrar al perder foco
        input.addEventListener("blur", () => {
            setTimeout(() => cerrarBox(box), 250);
        });
    }

    function cerrarBox(box) {
        box.innerHTML = "";
        box.style.display = "none";
    }

    function mostrarEnBox(box, html) {
        box.innerHTML = html;
        box.style.display = "block";
    }

    // ── Calcular total ────────────────────────────────────────────────────
    function calcularTotal() {
        let subtotal = 0;

        tableBody.querySelectorAll("tr:not(#emptyRow)").forEach(tr => {
            const cant = parseFloat(tr.querySelector(".cantidad")?.value) || 0;
            const prec = parseFloat(tr.querySelector(".precio")?.value)   || 0;
            const sub  = cant * prec;
            const cell = tr.querySelector(".subtotal");
            if (cell) cell.innerText = fmt(sub);
            subtotal += sub;
        });

        subtotal += parseFloat(manoObraInput?.value) || 0;

        if (domicilioCheckbox?.checked && envioInput) {
            subtotal += parseFloat(envioInput.value) || 0;
        }

        const ivaPct = parseFloat(ivaSelect?.value) || 0;
        const ivaAmt = subtotal * (ivaPct / 100);
        const total  = subtotal + ivaAmt;

        if (subtotalSpan) subtotalSpan.innerText = fmt(subtotal);
        if (ivaSpan)      ivaSpan.innerText      = `${fmt(ivaAmt)} (${ivaPct}%)`;
        if (totalSpan)    totalSpan.innerText     = fmt(total);

        const hiddenTotal = document.getElementById("hiddenTotal");
        if (hiddenTotal) hiddenTotal.value = total.toFixed(2);
    }

    // ── Fila vacía ────────────────────────────────────────────────────────
    function mostrarFilaVacia() {
        if (tableBody.querySelectorAll("tr:not(#emptyRow)").length === 0) {
            const tr = document.createElement("tr");
            tr.id = "emptyRow";
            tr.innerHTML = `<td colspan="5" class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-3 d-block mb-1"></i>
                No hay arreglos. Haz clic en <strong>Agregar arreglo</strong>.
            </td>`;
            tableBody.appendChild(tr);
            calcularTotal();
        }
    }

    // ── Formato moneda ────────────────────────────────────────────────────
    function fmt(n) {
        return "$" + n.toLocaleString("es-CO", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

});