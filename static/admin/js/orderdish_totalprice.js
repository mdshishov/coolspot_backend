document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        const priceInput = document.getElementById('id_dish_price');
        const amountInput = document.getElementById('id_quantity');
        const preview = document.getElementById('total_price_preview');

        if (!priceInput || !amountInput || !preview) {
            return;
        }

        function updateTotalPrice() {
            const price = parseFloat(priceInput.value) || 0;
            const amount = parseFloat(amountInput.value) || 0;
            preview.textContent = (price * amount).toFixed(2);
        }

        priceInput.addEventListener('input', updateTotalPrice);
        amountInput.addEventListener('input', updateTotalPrice);
    });
});