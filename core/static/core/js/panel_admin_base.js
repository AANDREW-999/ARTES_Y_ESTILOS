document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // Guardar estado en localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }
    
    // Restaurar estado del sidebar
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed');
    if (sidebarCollapsed === 'true') {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
    }
    
    // ==================== SIDEBAR RESPONSIVE ====================
    function handleResponsiveSidebar() {
        if (window.innerWidth <= 991) {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('expanded');
            
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('active');
            });
            
            // Cerrar sidebar al hacer clic fuera
            document.addEventListener('click', function(e) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('active');
                }
            });
        }
    }
    
    handleResponsiveSidebar();
    window.addEventListener('resize', handleResponsiveSidebar);
    
    // ==================== AUTO-CERRAR ALERTAS ====================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // ==================== MARCAR LINK ACTIVO EN SIDEBAR ====================
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // ==================== BÚSQUEDA EN TIEMPO REAL ====================
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            console.log('Buscando:', searchTerm);
            // Aquí puedes implementar la lógica de búsqueda
        });
    }
    
    // ==================== TOOLTIPS DE BOOTSTRAP ====================
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // ==================== CONFIRMACIÓN DE ELIMINACIÓN ====================
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que deseas eliminar este elemento?')) {
                e.preventDefault();
            }
        });
    });
    
    // ==================== FUNCIÓN PARA CARGAR GRÁFICOS ====================
    window.initDashboardChart = function(canvasId, data, options) {
        const ctx = document.getElementById(canvasId);
        if (ctx) {
            new Chart(ctx, {
                type: data.type || 'bar',
                data: data,
                options: options || {}
            });
        }
    };
    
    console.log('Dashboard inicializado correctamente');
});

// ==================== FUNCIONES GLOBALES ====================

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const messagesContainer = document.querySelector('.messages-container') || document.querySelector('.content-wrapper');
    if (messagesContainer) {
        messagesContainer.insertBefore(alertDiv, messagesContainer.firstChild);
        
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

// Función para confirmar acciones
function confirmAction(message) {
    return confirm(message || '¿Estás seguro de realizar esta acción?');
}

// Exportar funciones para uso global
window.showNotification = showNotification;
window.confirmAction = confirmAction;

document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // Guardar estado en localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }
    
    // Restaurar estado del sidebar
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed');
    if (sidebarCollapsed === 'true') {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
    }
    
    // ==================== SIDEBAR RESPONSIVE ====================
    function handleResponsiveSidebar() {
        if (window.innerWidth <= 991) {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('expanded');
            
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('active');
            });
            
            // Cerrar sidebar al hacer clic fuera
            document.addEventListener('click', function(e) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('active');
                }
            });
        }
    }
    
    handleResponsiveSidebar();
    window.addEventListener('resize', handleResponsiveSidebar);
    
    // ==================== AUTO-CERRAR ALERTAS ====================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // ==================== MARCAR LINK ACTIVO EN SIDEBAR ====================
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // ==================== SUBMENÚS DESPLEGABLES (COMPRAS, ETC.) ====================
    /**
     * Para cada submenú colapsable del sidebar:
     * 1. Si alguno de sus enlaces hijos coincide con la URL actual,
     *    se abre automáticamente y se marca el padre como "active".
     * 2. El estado abierto/cerrado se guarda en localStorage para
     *    que no se cierre al navegar entre páginas.
     * 3. Al cerrar el sidebar (collapse) se vuelve a abrir si
     *    el submenú estaba activo.
     */
    const submenuToggles = document.querySelectorAll('[data-bs-toggle="collapse"]');

    submenuToggles.forEach(toggle => {
        const targetId = toggle.getAttribute('href') || toggle.dataset.bsTarget;
        if (!targetId) return;

        const submenu = document.querySelector(targetId);
        if (!submenu) return;

        const storageKey = 'submenu_' + targetId.replace('#', '');

        // --- Detectar si algún hijo está activo ---
        const childLinks = submenu.querySelectorAll('.nav-link');
        let hasActiveChild = false;

        childLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.startsWith(href) && href !== '/') {
                link.classList.add('active');
                hasActiveChild = true;
            }
        });

        // --- Abrir el submenú si tiene hijo activo O si estaba abierto antes ---
        const wasOpen = localStorage.getItem(storageKey) === 'true';

        if (hasActiveChild || wasOpen) {
            submenu.classList.add('show');
            toggle.setAttribute('aria-expanded', 'true');
            toggle.classList.add('active');
        }

        // --- Guardar estado al abrir/cerrar manualmente ---
        submenu.addEventListener('show.bs.collapse', function() {
            localStorage.setItem(storageKey, 'true');
            toggle.classList.add('active');
        });

        submenu.addEventListener('hide.bs.collapse', function() {
            // Solo guardar "cerrado" si no tiene hijo activo
            if (!hasActiveChild) {
                localStorage.setItem(storageKey, 'false');
            }
            toggle.classList.remove('active');
        });
    });

    // ==================== BÚSQUEDA EN TIEMPO REAL ====================
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            console.log('Buscando:', searchTerm);
            // Aquí puedes implementar la lógica de búsqueda
        });
    }
    
    // ==================== TOOLTIPS DE BOOTSTRAP ====================
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // ==================== CONFIRMACIÓN DE ELIMINACIÓN ====================
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que deseas eliminar este elemento?')) {
                e.preventDefault();
            }
        });
    });
    
    // ==================== FUNCIÓN PARA CARGAR GRÁFICOS ====================
    window.initDashboardChart = function(canvasId, data, options) {
        const ctx = document.getElementById(canvasId);
        if (ctx) {
            new Chart(ctx, {
                type: data.type || 'bar',
                data: data,
                options: options || {}
            });
        }
    };
    
    console.log('Dashboard inicializado correctamente');
});

// ==================== FUNCIONES GLOBALES ====================

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const messagesContainer = document.querySelector('.messages-container') || document.querySelector('.content-wrapper');
    if (messagesContainer) {
        messagesContainer.insertBefore(alertDiv, messagesContainer.firstChild);
        
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

// Función para confirmar acciones
function confirmAction(message) {
    return confirm(message || '¿Estás seguro de realizar esta acción?');
}

// Exportar funciones para uso global
window.showNotification = showNotification;
window.confirmAction = confirmAction;