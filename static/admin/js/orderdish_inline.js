document.addEventListener('DOMContentLoaded', function () {
    function updateTotal(row) {

        const priceInput = row.querySelector('input[name$="-dish_price"]');
        const quantityInput = row.querySelector('input[name$="-quantity"]');

        const totalCell = row.querySelector('.field-total_price');

        if (!priceInput || !quantityInput || !totalCell) {
            return;
        }

        const price = parseFloat(priceInput.value || 0);
        const quantity = parseInt(quantityInput.value || 0);

        const total = price * quantity;

        totalCell.innerText = total.toFixed(2);
    }

    function bindRow(row) {
        const inputs = row.querySelectorAll(
            'input[name$="-dish_price"], input[name$="-quantity"]'
        );

        inputs.forEach(input => {
            input.addEventListener('input', () => updateTotal(row));
        });

        updateTotal(row);
    }

    setTimeout(() => {
        document.querySelectorAll('.dynamic-positions').forEach(bindRow);
    }, 0);
});