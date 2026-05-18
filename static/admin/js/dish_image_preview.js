document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        const input = document.querySelector('input[type="file"][name$="image"]');
        const previewContainer = document.getElementById('dish_image_preview');

        if (!input) return;

        let previewImg = previewContainer?.querySelector('img');
        if (!previewImg) {
            previewImg = document.createElement('img');
            previewImg.style.borderRadius = '4px';
            previewContainer.append(previewImg);
        }
        previewImg.style.height = '200px';

        input.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (e) {
                previewImg.src = e.target.result;
            };

            reader.readAsDataURL(file);
        });
    }, 0)

});