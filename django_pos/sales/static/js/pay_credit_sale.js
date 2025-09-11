document.addEventListener('DOMContentLoaded', function () {
    const paymentLinesContainer = document.getElementById('payment-lines-container');
    const addPaymentBtn = document.getElementById('add-payment-btn');
    const paymentLineTemplate = document.getElementById('payment-line-template');
    const paymentForm = document.getElementById('payment-form');
    const paymentsJsonInput = document.getElementById('payments-json-input');

    // Summary elements
    const summaryAmountToPay = document.getElementById('summary-amount-to-pay');
    const summaryTotalPaid = document.getElementById('summary-total-paid');
    const summaryChange = document.getElementById('summary-change');
    const summaryIgtf = document.getElementById('summary-igtf'); // Assuming this element will be added

    // Data from backend
    const saleBalance = parseFloat(summaryAmountToPay.textContent);
    const exchangeRate = parseFloat(paymentForm.dataset.exchangeRate) || 0;
    const igtfPercentage = parseFloat(paymentForm.dataset.igtfPercentage) || 0;

    function addPaymentLine() {
        const templateContent = paymentLineTemplate.content.cloneNode(true);
        paymentLinesContainer.appendChild(templateContent);
        // Add event listeners to new line
        const newLine = paymentLinesContainer.lastElementChild;
        newLine.querySelector('.remove-payment-btn').addEventListener('click', () => {
            newLine.remove();
            updateCalculations();
        });
        newLine.querySelector('.payment-amount').addEventListener('input', updateCalculations);
        newLine.querySelector('.payment-method-select').addEventListener('change', updateCalculations);
        updateCalculations();
    }

    function updateCalculations() {
        let totalPaidUSD = 0;
        let totalIGTF = 0;

        const paymentLines = paymentLinesContainer.querySelectorAll('.payment-line');
        paymentLines.forEach(line => {
            const amountInput = line.querySelector('.payment-amount');
            const amount = parseFloat(amountInput.value) || 0;
            const methodSelect = line.querySelector('.payment-method-select');
            const selectedOption = methodSelect.options[methodSelect.selectedIndex];
            const isForeign = selectedOption.dataset.isForeign === 'true';

            let amountInUSD = 0;
            if (isForeign) {
                amountInUSD = amount;
                // Apply IGTF for foreign currency payments
                totalIGTF += amount * (igtfPercentage / 100);
            } else {
                // Convert VES to USD
                amountInUSD = exchangeRate > 0 ? amount / exchangeRate : 0;
            }
            totalPaidUSD += amountInUSD;
        });

        const finalTotalPaid = totalPaidUSD + totalIGTF;
        const change = finalTotalPaid - saleBalance;

        summaryTotalPaid.textContent = finalTotalPaid.toFixed(2);
        if (summaryIgtf) summaryIgtf.textContent = totalIGTF.toFixed(2);
        summaryChange.textContent = change > 0 ? change.toFixed(2) : '0.00';
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

            if (parseFloat(amount) > 0) {
                payments.push({
                    payment_method_id: methodSelect.value,
                    amount: amount,
                    is_foreign: isForeign,
                    reference: reference
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
});