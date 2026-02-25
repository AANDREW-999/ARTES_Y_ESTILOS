document.addEventListener('DOMContentLoaded', function () {
    console.log("Script de validaciones y búsqueda cargado correctamente.");


    // 1. LÓGICA DE BÚSQUEDA (Filtro en Tabla)
   
    const buscador = document.getElementById('id_buscador');
    
    if (buscador) {
        buscador.addEventListener('keyup', function (e) {
            const termino = e.target.value.toLowerCase();
            // Seleccionamos todas las filas del cuerpo de la tabla
            const filas = document.querySelectorAll('table tbody tr');

            filas.forEach(fila => {
                // Columna 1: Nombre del Producto (índice 0)
                // Columna 2: Categoría (índice 1)
                // Usamos 'innerText' para obtener el texto limpio
                const textoNombre = fila.cells[0].innerText.toLowerCase();
                const textoCategoria = fila.cells[1].innerText.toLowerCase();

                // Si el término está en el nombre O en la categoría, mostramos la fila
                if (textoNombre.includes(termino) || textoCategoria.includes(termino)) {
                    fila.style.display = '';
                } else {
                    fila.style.display = 'none';
                }
            });
        });
    }

    // 2. VALIDACIONES DEL MODAL 

    
    // Validación Nombre: Solo letras y espacios
    const inputNombre = document.getElementById('inputNombre');
    if (inputNombre) {
        inputNombre.addEventListener('input', function (e) {
            // Reemplaza todo lo que NO sea letras (incluye tildes y ñ)
            this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
        });
    }

    // Validación Precio: Solo números, punto y coma
    const inputPrecio = document.getElementById('inputPrecio');
    if (inputPrecio) {
        inputPrecio.addEventListener('input', function (e) {
            // Reemplaza todo lo que NO sea números, punto o coma
            this.value = this.value.replace(/[^0-9.,]/g, '');
        });
    }
});