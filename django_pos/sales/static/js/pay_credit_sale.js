document.addEventListener('DOMContentLoaded', function () {
    const paymentLinesContainer = document.getElementById('payment-lines-container');
    const addPaymentBtn = document.getElementById('add-payment-btn');
    const paymentLineTemplate = document.getElementById('payment-line-template');
    const paymentForm = document.getElementById('payment-form');
    const paymentsJsonInput = document.getElementById('payments-json-input');

    // Data from backend
    const defaultExchangeRate = parseFloat(paymentForm.dataset.exchangeRate.replace(',', '.')) || 0;

    function addPaymentLine() {
        const templateContent = paymentLineTemplate.content.cloneNode(true);
        
        const dateInput = templateContent.querySelector('.payment-date');
        dateInput.valueAsDate = new Date();

        const exchangeRateInput = templateContent.querySelector('.payment-exchange-rate');
        exchangeRateInput.value = defaultExchangeRate.toFixed(2);

        paymentLinesContainer.appendChild(templateContent);
        
        const newLine = paymentLinesContainer.lastElementChild;
        newLine.querySelector('.remove-payment-btn').addEventListener('click', () => {
            newLine.remove();
        });
    }

    addPaymentBtn.addEventListener('click', addPaymentLine);

    paymentForm.addEventListener('submit', function (e) {
        const payments = [];
        const paymentLines = paymentLinesContainer.querySelectorAll('.payment-line');

        paymentLines.forEach(line => {
            const methodSelect = line.querySelector('.payment-method-select');
            const selectedOption = methodSelect.options[methodSelect.selectedIndex];
            const isForeign = selectedOption.dataset.isForeign === 'true';
            const amount = line.querySelector('.payment-amount').value;
            const reference = line.querySelector('.payment-reference').value;
            const exchangeRate = line.querySelector('.payment-exchange-rate').value;
            const paymentDate = line.querySelector('.payment-date').value;

            if (parseFloat(amount) > 0) {
                payments.push({
                    payment_method_id: methodSelect.value,
                    amount: amount,
                    is_foreign: isForeign,
                    reference: reference,
                    exchange_rate: exchangeRate,
                    payment_date: paymentDate
                });
            }
        });

        if (payments.length === 0) {
            e.preventDefault();
            alert('You must add at least one payment.');
            return;
        }

        paymentsJsonInput.value = JSON.stringify(payments);
    });

    // Add one payment line by default
    addPaymentLine();

    // Calculate and set the VES balance
    const balanceUsdEl = document.getElementById('sale-balance-usd');
    const balanceVesEl = document.getElementById('sale-balance-ves');

    if (balanceUsdEl && balanceVesEl && defaultExchangeRate) {
        const balanceUsd = parseFloat(balanceUsdEl.textContent);
        const balanceVes = balanceUsd * defaultExchangeRate;
        balanceVesEl.textContent = `Bs. ${balanceVes.toFixed(2)}`;
    }
});