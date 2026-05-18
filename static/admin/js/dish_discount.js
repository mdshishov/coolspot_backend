document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        const priceInput = document.getElementById('id_price');
        const discountInput = document.getElementById('id_discount_percent');
        const preview = document.getElementById('final_price_preview');

        if (!priceInput || !discountInput || !preview) {
            return;
        }

        function updateDiscountPrice() {
            const price = parseFloat(priceInput.value) || 0;
            const discount = parseFloat(discountInput.value) || 0;

            if (!price) {
                preview.textContent = '0';
                return;
            }

            const result = Math.round(
                price * (100 - discount) / 100
            );

            preview.textContent = result;
        }

        priceInput.addEventListener('input', updateDiscountPrice);
        discountInput.addEventListener('input', updateDiscountPrice);

        updateDiscountPrice();
    });
});