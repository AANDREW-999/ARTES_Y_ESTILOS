from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def accesibilidad_widget():
    return mark_safe('''
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link rel="stylesheet" href="/static/accessibility/css/accesibility.css">
        <link rel="stylesheet" href="/static/accessibility/css/daltonismo.css">
        
        <div class="minegate-acc-trigger floral-theme" onclick="toggleAccPanel()" title="Opciones de Accesibilidad">
            <i class="fas fa-universal-access"></i>
            <div class="flower-decoration"></div>
        </div>

        <div id="accPanel" class="acc-widget-panel floral-panel" style="display: none; max-height: 80vh; overflow-y: auto;">
            <div class="panel-header">
                <i class="fas fa-seedling panel-icon"></i>
                <h5 class="panel-title">Herramientas de Accesibilidad</h5>
                <i class="fas fa-leaf panel-icon"></i>
            </div>
            
            <div class="acc-btn-group floral-grid">
                <button class="acc-opt floral-btn color-2" onclick="adjustFont(1)">
                    <div class="btn-content"><i class="fas fa-plus"></i><span>Aumentar letra</span></div>
                </button>
                
                <button class="acc-opt floral-btn color-3" onclick="adjustFont(-1)">
                    <div class="btn-content"><i class="fas fa-minus"></i><span>Disminuir letra</span></div>
                </button>
                
                <button class="acc-opt floral-btn color-4" onclick="toggleFeature('extra-spacing')">
                    <div class="btn-content"><i class="fas fa-arrows-alt-h"></i><span>Espacio</span></div>
                </button>
                
                <button class="acc-opt floral-btn color-1" onclick="toggleFeature('underline-links')">
                    <div class="btn-content"><i class="fas fa-link"></i><span>Enlaces</span></div>
                </button>
                
                <button class="acc-opt floral-btn color-2" onclick="toggleFeature('big-cursor')">
                    <div class="btn-content"><i class="fas fa-mouse-pointer"></i><span>Cursor</span></div>
                </button>

                <button class="acc-opt floral-btn color-5" onclick="handleColorBlind()">
                    <div class="btn-content"><i class="fas fa-eye"></i><span>Daltonismo</span></div>
                </button>
                
                <button class="acc-opt floral-btn reset-btn" onclick="resetAll()">
                    <div class="btn-content"><i class="fas fa-sync-alt"></i><span>Restablecer</span></div>
                </button>
            </div>
            
            <div class="panel-footer">
                <i class="fas fa-spa"></i>
            </div>
        </div>

        <div id="reading-guide"></div>

        <script src="/static/accessibility/js/accessibility.js"></script>
    ''')
