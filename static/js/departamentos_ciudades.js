(function () {
    'use strict';

    const API_BASE = 'https://api-colombia.com/api/v1';

    /** @type {Promise<Array<{id:number,name:string}>> | null} */
    let departmentsPromise = null;

    /** @type {Map<number, Promise<Array<{name:string}>>>} */
    const citiesByDepartmentId = new Map();

    function isNonEmptyString(value) {
        return typeof value === 'string' && value.trim().length > 0;
    }

    function setSelectOptions(selectEl, options) {
        selectEl.innerHTML = '';
        for (const opt of options) {
            const option = document.createElement('option');
            option.value = opt.value;
            option.textContent = opt.text;
            if (opt.disabled) option.disabled = true;
            if (opt.selected) option.selected = true;
            if (opt.dataset) {
                for (const [k, v] of Object.entries(opt.dataset)) {
                    option.dataset[k] = String(v);
                }
            }
            selectEl.appendChild(option);
        }
    }

    async function fetchJson(url, { signal } = {}) {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
            signal,
        });

        if (!response.ok) {
            const text = await response.text().catch(() => '');
            throw new Error(`HTTP ${response.status} al consultar ${url}${text ? `: ${text}` : ''}`);
        }

        return response.json();
    }

    function getDepartments() {
        if (!departmentsPromise) {
            departmentsPromise = fetchJson(`${API_BASE}/Department`)
                .then((data) => {
                    if (!Array.isArray(data)) return [];
                    return data
                        .filter((d) => d && typeof d === 'object')
                        .map((d) => ({ id: d.id, name: d.name }))
                        .filter((d) => Number.isFinite(d.id) && isNonEmptyString(d.name))
                        .sort((a, b) => a.name.localeCompare(b.name, 'es'));
                })
                .catch((err) => {
                    // Permitir reintentos posteriores si falla la carga inicial.
                    departmentsPromise = null;
                    throw err;
                });
        }
        return departmentsPromise;
    }

    function getCities(departmentId, { signal } = {}) {
        const idNum = Number(departmentId);
        if (!Number.isFinite(idNum)) {
            return Promise.resolve([]);
        }

        if (!citiesByDepartmentId.has(idNum)) {
            const promise = fetchJson(`${API_BASE}/Department/${idNum}/cities`, { signal })
                .then((data) => {
                    if (!Array.isArray(data)) return [];
                    return data
                        .filter((c) => c && typeof c === 'object')
                        .map((c) => ({ name: c.name }))
                        .filter((c) => isNonEmptyString(c.name))
                        .sort((a, b) => a.name.localeCompare(b.name, 'es'));
                })
                .catch((err) => {
                    // Si aborta o falla, no dejamos un Promise rechazado cacheado.
                    citiesByDepartmentId.delete(idNum);
                    throw err;
                });
            citiesByDepartmentId.set(idNum, promise);
        }

        return citiesByDepartmentId.get(idNum);
    }

    function findPairedCitySelect(departSelect) {
        const form = departSelect.closest('form');
        if (form) {
            const cityInForm = form.querySelector('select.js-ciudad');
            if (cityInForm) return cityInForm;
        }
        return document.querySelector('select.js-ciudad');
    }

    function readInitialValue(container, id) {
        const el = container.querySelector(`#${id}`);
        if (!el) return '';
        return String(el.value || '').trim();
    }

    function getSelectedDepartmentId(departSelect) {
        const value = String(departSelect.value || '').trim();
        const id = Number(value);
        return Number.isFinite(id) && value !== '' ? id : null;
    }

    function applyInitialDepartmentValue(departSelect, departments, initialValue) {
        const raw = String(initialValue || '').trim();
        if (!raw) return;

        // Si ya viene como id (nuevo formato), seleccionarlo directo.
        const maybeId = Number(raw);
        if (Number.isFinite(maybeId) && raw !== '') {
            departSelect.value = String(maybeId);
            return;
        }

        // Si viene como nombre (formato antiguo), mapear por nombre.
        const target = raw.toLocaleLowerCase('es');
        const match = departments.find((d) => String(d.name).trim().toLocaleLowerCase('es') === target);
        if (match) {
            departSelect.value = String(match.id);
        }
    }

    async function initPair(departSelect) {
        const citySelect = findPairedCitySelect(departSelect);
        if (!citySelect) return;

        const container = departSelect.closest('form') || document;

        const initialDepartmentName = readInitialValue(container, 'id_departamento_original');
        const initialCityName = readInitialValue(container, 'id_ciudad_original');

        // Estado inicial UI
        departSelect.classList.add('js-departamento');
        citySelect.classList.add('js-ciudad');

        setSelectOptions(departSelect, [
            { value: '', text: 'Cargando departamentos...', disabled: true, selected: true },
        ]);

        citySelect.disabled = true;
        setSelectOptions(citySelect, [
            { value: '', text: 'Seleccione una ciudad', selected: true },
        ]);

        let departments;
        try {
            departments = await getDepartments();
        } catch (err) {
            console.error('Error cargando departamentos:', err);
            setSelectOptions(departSelect, [
                { value: '', text: 'Error al cargar departamentos', disabled: true, selected: true },
            ]);
            citySelect.disabled = true;
            return;
        }

        const deptOptions = [{ value: '', text: 'Seleccione un departamento' }];
        for (const d of departments) {
            deptOptions.push({
                value: String(d.id),
                text: d.name,
            });
        }
        setSelectOptions(departSelect, deptOptions);

        if (isNonEmptyString(initialDepartmentName)) {
            applyInitialDepartmentValue(departSelect, departments, initialDepartmentName);
        }

        async function loadCitiesForCurrentDepartment({ preferCity } = {}) {
            const selectedDepartmentId = getSelectedDepartmentId(departSelect);

            // Reset cities
            citySelect.disabled = true;
            setSelectOptions(citySelect, [
                { value: '', text: selectedDepartmentId ? 'Cargando ciudades...' : 'Seleccione una ciudad', disabled: !!selectedDepartmentId, selected: true },
            ]);

            if (!selectedDepartmentId) {
                citySelect.disabled = true;
                return;
            }

            const abortController = new AbortController();
            loadCitiesForCurrentDepartment._abort?.();
            loadCitiesForCurrentDepartment._abort = () => abortController.abort();

            let cities;
            try {
                cities = await getCities(selectedDepartmentId, { signal: abortController.signal });
            } catch (err) {
                if (err && err.name === 'AbortError') return;
                console.error('Error cargando ciudades:', err);
                citySelect.disabled = true;
                setSelectOptions(citySelect, [
                    { value: '', text: 'Error al cargar ciudades', disabled: true, selected: true },
                ]);
                return;
            }

            const cityOptions = [{ value: '', text: 'Seleccione una ciudad' }];
            for (const c of cities) {
                cityOptions.push({ value: c.name, text: c.name });
            }
            setSelectOptions(citySelect, cityOptions);
            citySelect.disabled = false;

            const preferred = isNonEmptyString(preferCity) ? preferCity : '';
            if (preferred) {
                citySelect.value = preferred;
            }
        }

        departSelect.addEventListener('change', function () {
            loadCitiesForCurrentDepartment({ preferCity: '' });
        });

        // Si hay valores iniciales (edición / reenvío), precargar ciudades.
        if (getSelectedDepartmentId(departSelect)) {
            await loadCitiesForCurrentDepartment({ preferCity: initialCityName });
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        const departamentoSelects = Array.from(document.querySelectorAll('select.js-departamento, select#id_departamento'));
        if (departamentoSelects.length === 0) return;

        // Evitar inicializar dos veces el mismo select.
        const uniques = Array.from(new Set(departamentoSelects));
        uniques.forEach((departSelect) => {
            // No bloquear el resto si una pareja falla.
            initPair(departSelect).catch((err) => {
                console.error('Error inicializando departamento/ciudad:', err);
            });
        });
    });
})();
