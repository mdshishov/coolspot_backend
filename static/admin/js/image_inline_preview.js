document.addEventListener('DOMContentLoaded', function () {
    function attachPreview(row) {
        const fileInput = row.querySelector('input[type="file"]');
        if (!fileInput) return;

        const previewContainer = row.querySelector('.inline_image_preview');
        let previewImg = previewContainer?.querySelector('img');
        if (!previewImg) {
            previewImg = document.createElement('img');
            previewImg.style.borderRadius = '4px';
            previewImg.style.height = '100px';
            previewContainer.append(previewImg);
        }

        fileInput.addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (e) {
                previewImg.src = e.target.result;
            };

            reader.readAsDataURL(file);
        });
    }

    function initAllRows() {
        document.querySelectorAll('.dynamic-images').forEach(row => {
            attachPreview(row);
        });
    }

    setTimeout(initAllRows, 0);

    document.body.addEventListener('formset:added', function (e) {
        attachPreview(event.target);
    });

});