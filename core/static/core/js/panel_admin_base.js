document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
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
    
    // Sidebar responsive
    function handleResponsiveSidebar() {
        if (window.innerWidth <= 991) {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('expanded');
            
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('active');
            });
            
            document.addEventListener('click', function(e) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('active');
                }
            });
        }
    }
    
    handleResponsiveSidebar();
    window.addEventListener('resize', handleResponsiveSidebar);
    
    // Auto-cerrar alertas
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Marcar link activo en sidebar
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Submenús desplegables (Compras, etc.)
    const submenuToggles = document.querySelectorAll('[data-bs-toggle="collapse"]');

    submenuToggles.forEach(toggle => {
        const targetId = toggle.getAttribute('href') || toggle.dataset.bsTarget;
        if (!targetId) return;

        const submenu = document.querySelector(targetId);
        if (!submenu) return;

        const storageKey = 'submenu_' + targetId.replace('#', '');

        // Detectar si algún hijo está activo
        const childLinks = submenu.querySelectorAll('.nav-link');
        let hasActiveChild = false;

        childLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.startsWith(href) && href !== '/') {
                link.classList.add('active');
                hasActiveChild = true;
            }
        });

        // Abrir el submenú si tiene hijo activo O si estaba abierto antes
        const wasOpen = localStorage.getItem(storageKey) === 'true';

        if (hasActiveChild || wasOpen) {
            submenu.classList.add('show');
            toggle.setAttribute('aria-expanded', 'true');
            toggle.classList.add('active');
        }

        // Guardar estado al abrir/cerrar manualmente
        submenu.addEventListener('show.bs.collapse', function() {
            localStorage.setItem(storageKey, 'true');
            toggle.classList.add('active');
        });

        submenu.addEventListener('hide.bs.collapse', function() {
            if (!hasActiveChild) {
                localStorage.setItem(storageKey, 'false');
            }
            toggle.classList.remove('active');
        });
    });

    // Búsqueda en tiempo real
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            console.log('Buscando:', searchTerm);
        });
    }
    
    // Tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Confirmación de eliminación
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que deseas eliminar este elemento?')) {
                e.preventDefault();
            }
        });
    });
    
    // Función para cargar gráficos
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

// Funciones globales
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

function confirmAction(message) {
    return confirm(message || '¿Estás seguro de realizar esta acción?');
}

window.showNotification = showNotification;
window.confirmAction = confirmAction;