document.addEventListener('DOMContentLoaded', function () {

    let cropper;
    let flipH = 1;
    let flipV = 1;

    const imageInput       = document.getElementById('image-input');
    const imagePreview     = document.getElementById('image-preview');
    const cropperWrapper   = document.getElementById('cropper-wrapper');
    const croppedDataInput = document.getElementById('cropped-image-data');
    const productForm      = document.getElementById('product-form');
    const previewBox       = document.getElementById('crop-preview');

    // ── Selección de imagen ────────────────────────────────────────
    if (imageInput) {
        imageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];

            if (!file || !file.type.startsWith('image/')) return;

            const reader = new FileReader();
            reader.onload = function (event) {
                imagePreview.src = event.target.result;
                cropperWrapper.style.display = 'block';

                // Destruir instancia anterior si existe
                if (cropper) { cropper.destroy(); cropper = null; }

                // Reiniciar estados de flip
                flipH = 1;
                flipV = 1;

                // Inicializar Cropper.js
                cropper = new Cropper(imagePreview, {
                    aspectRatio: 1,          // cuadrado — ideal para catálogo
                    viewMode: 1,
                    autoCropArea: 0.9,
                    checkOrientation: false,
                    preview: previewBox,     // mini preview en tiempo real
                    ready: function () {
                        cropperWrapper.style.opacity = '0';
                        cropperWrapper.style.transition = 'opacity .3s ease';
                        requestAnimationFrame(() => {
                            cropperWrapper.style.opacity = '1';
                        });
                    }
                });
            };
            reader.readAsDataURL(file);
        });
    }

    // ── Botones de transformación ──────────────────────────────────
    const btnRotateLeft  = document.getElementById('btn-rotate-left');
    const btnRotateRight = document.getElementById('btn-rotate-right');
    const btnFlipH       = document.getElementById('btn-flip-h');
    const btnFlipV       = document.getElementById('btn-flip-v');

    if (btnRotateLeft)  btnRotateLeft.addEventListener('click',  () => cropper && cropper.rotate(-90));
    if (btnRotateRight) btnRotateRight.addEventListener('click', () => cropper && cropper.rotate(90));

    if (btnFlipH) btnFlipH.addEventListener('click', function () {
        if (!cropper) return;
        flipH *= -1;
        cropper.scaleX(flipH);
    });

    if (btnFlipV) btnFlipV.addEventListener('click', function () {
        if (!cropper) return;
        flipV *= -1;
        cropper.scaleY(flipV);
    });

    // ── Submit: convertir recorte a Base64 ────────────────────────
    // Django recibe el Base64 en 'cropped_image_data' y lo guarda en MEDIA_ROOT
    if (productForm) {
        productForm.addEventListener('submit', function () {
            if (!cropper) return;  // sin cropper activo → envía imagen original

            const canvas = cropper.getCroppedCanvas({
                width:  600,
                height: 600,
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });

            if (canvas) {
                croppedDataInput.value = canvas.toDataURL('image/jpeg', 0.85);
            }
        });
    }

});