let fontSizeFactor = 100;
let filterStates = {
    'underline-links': false,
    'big-cursor': false,
    'extra-spacing': false,
    'high-contrast-mode': false,
    'color-blind-mode': false
};
let colorBlindType = 'none';
let isReading = false;
let guideEnabled = false;
let guideElement = null;
let colorBlindMenuOpen = false;

document.addEventListener('DOMContentLoaded', () => {
    createContentWrapper();
    loadSettings();
    initializeReadingGuide();
    setupEventListeners();
    applyAccessibilityChanges();
});

// Crear contenedor wrapper para aislar efectos del widget
function createContentWrapper() {
    if (document.getElementById('accessibility-content-wrapper')) return;
    if (document.querySelector('[data-wrapper-done]')) return;
    
    const wrapper = document.createElement('div');
    wrapper.id = 'accessibility-content-wrapper';
    wrapper.dataset.wrapperDone = 'true';
    
    // Obtener todos los elementos del body excepto el widget de accesibilidad
    const allChildren = Array.from(document.body.children);
    
    allChildren.forEach(child => {
        // NO mover: botón, panel, guía y scripts del widget
        if (child.classList?.contains('minegate-acc-trigger') || 
            child.id === 'accPanel' || 
            child.id === 'reading-guide' ||
            child.tagName === 'SCRIPT' ||
            child.classList?.contains('color-blind-btn-wrapper')) {
            return;
        }
        wrapper.appendChild(child);
    });
    
    document.body.insertBefore(wrapper, document.body.firstChild);
}

function loadSettings() {
    fontSizeFactor = parseInt(localStorage.getItem('mg-font')) || 100;
    colorBlindType = localStorage.getItem('mg-colorblind-type') || 'none';
    
    Object.keys(filterStates).forEach(filter => {
        filterStates[filter] = localStorage.getItem('mg-' + filter) === 'true';
    });
    
    if (colorBlindType !== 'none') {
        filterStates['color-blind-mode'] = true;
    }
}

function initializeReadingGuide() {
    guideElement = document.getElementById('reading-guide');
    if (!guideElement) {
        guideElement = document.createElement('div');
        guideElement.id = 'reading-guide';
        guideElement.style.cssText = 'display: none; position: fixed; height: 12px; width: 100%; background: rgba(255, 235, 0, 0.7); z-index: 2147483647; pointer-events: none; top: 0; left: 0; box-shadow: 0 0 12px rgba(255, 255, 0, 0.9); border-bottom: 2px solid #ffd600;';
        document.body.appendChild(guideElement);
    }
}

function setupEventListeners() {
    window.addEventListener('mousemove', (e) => {
        if (guideEnabled && guideElement) {
            guideElement.style.top = e.clientY + 'px';
        }
    });

    document.addEventListener('click', (e) => {
        const panel = document.getElementById('accPanel');
        const trigger = document.querySelector('.minegate-acc-trigger');
        const colorBlindMenu = document.getElementById('colorBlindMenu');
        
        // Cerrar panel si se hace clic fuera
        if (panel && trigger && !panel.contains(e.target) && !trigger.contains(e.target)) {
            panel.style.display = 'none';
        }
        
        // Cerrar menú de daltonismo si se hace clic fuera
        if (colorBlindMenu && !e.target.closest('.color-blind-btn-wrapper')) {
            colorBlindMenu.style.display = 'none';
            colorBlindMenuOpen = false;
        }
    });
}

// FUNCIONES PRINCIPALES

function toggleAccPanel() {
    const panel = document.getElementById('accPanel');
    if (!panel) return;
    
    const isVisible = panel.style.display === 'block';
    panel.style.display = isVisible ? 'none' : 'block';
    
    // Cerrar menú de daltonismo al cerrar el panel
    if (isVisible) {
        const menu = document.getElementById('colorBlindMenu');
        if (menu) {
            menu.style.display = 'none';
            colorBlindMenuOpen = false;
        }
    }
}

function adjustFont(dir) {
    fontSizeFactor += (dir * 10);
    fontSizeFactor = Math.max(70, Math.min(150, fontSizeFactor));
    localStorage.setItem('mg-font', fontSizeFactor);
    applyAccessibilityChanges();
}

function toggleFeature(className) {
    filterStates[className] = !filterStates[className];
    localStorage.setItem('mg-' + className, filterStates[className]);
    applyAccessibilityChanges();
}

function toggleColorBlindMenu(event) {
    if (event) event.stopPropagation();
    
    const menu = document.getElementById('colorBlindMenu');
    if (!menu) return;
    
    colorBlindMenuOpen = !colorBlindMenuOpen;
    menu.style.display = colorBlindMenuOpen ? 'block' : 'none';
}

function setColorBlindType(type) {
    colorBlindType = type;
    localStorage.setItem('mg-colorblind-type', type);
    filterStates['color-blind-mode'] = (type !== 'none');
    
    // Cerrar menú
    const menu = document.getElementById('colorBlindMenu');
    if (menu) {
        menu.style.display = 'none';
        colorBlindMenuOpen = false;
    }
    
    applyAccessibilityChanges();

    // Fallback: aplicar filtro inline al wrapper por si la clase CSS no aplica
    const wrapper = document.getElementById('accessibility-content-wrapper') || document.body;
    const filterUrl = getColorBlindFilterUrl(type);
    try {
        wrapper.style.filter = filterUrl || '';
    } catch (e) {
        console.error('No se pudo aplicar el filtro inline:', e);
    }
}

function getColorBlindFilterUrl(type) {
    if (!type || type === 'none') return '';
    const map = {
        'protanopia': "url('data:image/svg+xml,\n<svg xmlns=\\\"http://www.w3.org/2000/svg\\\">\n  <filter id=\\\"protanopia\\\">\n    <feColorMatrix type=\\\"matrix\\\" values=\\\"0.567 0.433 0 0 0 0.558 0.442 0 0 0 0 0.242 0.758 0 0 0 0 0 1 0\\\"/>\n  </filter>\n</svg>#protanopia')",
        'deuteranopia': "url('data:image/svg+xml,\n<svg xmlns=\\\"http://www.w3.org/2000/svg\\\">\n  <filter id=\\\"deuteranopia\\\">\n    <feColorMatrix type=\\\"matrix\\\" values=\\\"0.625 0.375 0 0 0 0.7 0.3 0 0 0 0 0.3 0.7 0 0 0 0 0 1 0\\\"/>\n  </filter>\n</svg>#deuteranopia')",
        'tritanopia': "url('data:image/svg+xml,\n<svg xmlns=\\\"http://www.w3.org/2000/svg\\\">\n  <filter id=\\\"tritanopia\\\">\n    <feColorMatrix type=\\\"matrix\\\" values=\\\"0.95 0.05 0 0 0 0 0.433 0.567 0 0 0 0.475 0.525 0 0 0 0 0 1 0\\\"/>\n  </filter>\n</svg>#tritanopia')"
    };
    return map[type] || '';
}

function toggleReadingGuide() {
    guideEnabled = !guideEnabled;
    if (guideElement) {
        guideElement.style.display = guideEnabled ? 'block' : 'none';
    }
}

function handleTextToSpeech() {
    if (!isReading) {
        const text = window.getSelection().toString() || document.body.innerText;
        if (!text.trim()) return;

        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'es-ES';
        msg.onend = () => isReading = false;
        msg.onerror = () => isReading = false;
        window.speechSynthesis.speak(msg);
        isReading = true;
    } else {
        window.speechSynthesis.cancel();
        isReading = false;
    }
}

function resetAll() {
    // Resetear valores
    fontSizeFactor = 100;
    colorBlindType = 'none';
    Object.keys(filterStates).forEach(key => filterStates[key] = false);
    
    // Limpiar storage
    localStorage.clear();
    
    // Desactivar guía
    guideEnabled = false;
    if (guideElement) guideElement.style.display = 'none';
    
    // Cerrar menús
    const menu = document.getElementById('colorBlindMenu');
    if (menu) {
        menu.style.display = 'none';
        colorBlindMenuOpen = false;
    }
    
    // Detener voz
    window.speechSynthesis.cancel();
    isReading = false;
    
    applyAccessibilityChanges();
    
    // Cerrar panel
    const panel = document.getElementById('accPanel');
    if (panel) panel.style.display = 'none';
}

// APLICAR CAMBIOS

function applyAccessibilityChanges() {
    // Cambiar tamaño de fuente
    document.documentElement.style.fontSize = fontSizeFactor + "%";
    
    // Obtener contenedor objetivo
    const wrapper = document.getElementById('accessibility-content-wrapper') || document.body;
    
    // Aplicar/remover clases
    wrapper.classList.toggle('underline-links', filterStates['underline-links']);
    wrapper.classList.toggle('big-cursor', filterStates['big-cursor']);
    wrapper.classList.toggle('extra-spacing', filterStates['extra-spacing']);
    wrapper.classList.toggle('high-contrast-mode', filterStates['high-contrast-mode']);
    
    // Daltonismo
    wrapper.classList.remove('color-blind-protanopia', 'color-blind-deuteranopia', 'color-blind-tritanopia');
    if (filterStates['color-blind-mode'] && colorBlindType !== 'none') {
        wrapper.classList.add(`color-blind-${colorBlindType}`);
    }
    
    // Aplicar filtro inline también (fallback)
    try {
        wrapper.style.filter = (filterStates['color-blind-mode'] && colorBlindType !== 'none') ? getColorBlindFilterUrl(colorBlindType) : '';
    } catch (e) {
        console.error('Error aplicando filtro inline en applyAccessibilityChanges:', e);
    }
    // Actualizar UI
    updateButtonStates();
    updateColorBlindButtonText();
    updateColorBlindMenuStates();
}

function updateButtonStates() {
    document.querySelectorAll('.floral-btn').forEach(btn => {
        const onclick = btn.getAttribute('onclick');
        if (!onclick) return;
        
        // Botones con toggleFeature
        const featureMatch = onclick.match(/toggleFeature\('([^']+)'\)/);
        if (featureMatch) {
            btn.classList.toggle('active', filterStates[featureMatch[1]]);
            return;
        }
        
        // Botón de daltonismo
        if (btn.classList.contains('color-blind-btn')) {
            btn.classList.toggle('active', filterStates['color-blind-mode'] && colorBlindType !== 'none');
        }
    });
}

function updateColorBlindButtonText() {
    const btn = document.querySelector('.color-blind-btn .btn-content span');
    if (!btn) return;
    
    const typeNames = {
        'none': 'Daltonismo',
        'protanopia': 'Protanopía',
        'deuteranopia': 'Deuteranopía',
        'tritanopia': 'Tritanopía'
    };
    btn.textContent = typeNames[colorBlindType] || 'Daltonismo';
}

function updateColorBlindMenuStates() {
    document.querySelectorAll('.color-blind-menu-item').forEach(item => {
        const onclick = item.getAttribute('onclick');
        if (!onclick) return;
        
        const match = onclick.match(/setColorBlindType\('([^']+)'\)/);
        if (match) {
            item.classList.toggle('active', match[1] === colorBlindType);
        }
    });
}