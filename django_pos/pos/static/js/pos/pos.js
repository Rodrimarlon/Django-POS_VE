document.addEventListener('DOMContentLoaded', function () {
    console.log("Advanced POS JavaScript loaded!");

    // --- STATE ---
    const state = {
        products: [],
        cart: [],
        exchangeRate: 0,
        isLeftPanelActive: false,
        selectedCustomer: null,
        paymentMethods: [],
        currentPayments: [],
    };

    // --- DOM ELEMENTS ---
    const productListEl = document.getElementById('product-list');
    const categoryButtonsEl = document.getElementById('category-buttons');
    const categoryDropdownEl = document.getElementById('category-dropdown');
    const searchInput = document.getElementById('product-search');
    const orderlinesBodyEl = document.getElementById('orderlines-body');
    const totalUsdEl = document.getElementById('total-usd');
    const totalVesEl = document.getElementById('total-ves');
    const panelSwitcherBtn = document.getElementById('panel-switcher');
    const leftPane = document.querySelector('.left-pane');
    const rightPane = document.querySelector('.right-pane');
    const switcherIcon = panelSwitcherBtn ? panelSwitcherBtn.querySelector('i') : null;
    const customerBtn = document.getElementById('btn-customer');
    const customerBtnText = customerBtn.querySelector('span');
    const customerModal = new bootstrap.Modal(document.getElementById('customer-modal'));
    const newCustomerModal = new bootstrap.Modal(document.getElementById('new-customer-modal'));
    const customerSearchInput = document.getElementById('customer-search-input');
    const customerListEl = document.getElementById('customer-list');
    const addNewCustomerBtn = document.getElementById('add-new-customer-btn');
    const saveNewCustomerBtn = document.getElementById('save-new-customer-btn');
    const newCustomerForm = document.getElementById('new-customer-form');
    const paymentModal = new bootstrap.Modal(document.getElementById('payment-modal'));
    const paymentBtn = document.querySelector('.btn-payment');
    const paymentTotalUsdEl = document.getElementById('payment-total-usd');
    const paymentTotalVesEl = document.getElementById('payment-total-ves');
    const paymentRemainingUsdEl = document.getElementById('payment-remaining-usd');
    const paymentMethodsButtonsEl = document.getElementById('payment-methods-buttons');
    const paymentAmountInput = document.getElementById('payment-amount');
    const paymentReferenceInput = document.getElementById('payment-reference');
    const addPaymentBtn = document.getElementById('add-payment-btn');
    const paymentLinesListEl = document.getElementById('payment-lines-list');
    const paymentChangeUsdEl = document.getElementById('payment-change-usd');
    const creditSaleBtn = document.getElementById('credit-sale-btn');
    const finalizePaymentBtn = document.getElementById('finalize-payment-btn');

    // --- API FUNCTIONS ---
    async function fetchProducts(search = '', category = '') {
        try {
            const url = JSON.parse(document.getElementById('product_list_api_url').textContent);
            const response = await fetch(`${url}?search=${search}&category=${category}`);
            const data = await response.json();
            state.products = data.products;
            renderProducts(state.products);
        } catch (error) {
            console.error('Error fetching products:', error);
        }
    }

    async function fetchCategories() {
        try {
            const url = JSON.parse(document.getElementById('categories_list_api_url').textContent);
            const response = await fetch(url);
            const categories = await response.json();
            renderCategories(categories);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    }

    async function fetchCustomers(search = '') {
        try {
            const url = JSON.parse(document.getElementById('get_customers_api_url').textContent);
            const response = await fetch(`${url}?search=${search}`);
            const customers = await response.json();
            renderCustomers(customers);
        } catch (error) {
            console.error('Error fetching customers:', error);
        }
    }

    async function createCustomer(customerData) {
        try {
            const url = JSON.parse(document.getElementById('create_customer_api_url').textContent);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(customerData),
            });
            const data = await response.json();
            if (data.status === 'success') {
                handleCustomerSelect(data.customer);
                newCustomerModal.hide();
            } else {
                console.error('Error creating customer:', data.message);
            }
        } catch (error) {
            console.error('Error creating customer:', error);
        }
    }

    async function fetchPaymentMethods() {
        try {
            const url = JSON.parse(document.getElementById('payment_methods_list_api_url').textContent);
            const response = await fetch(url);
            const data = await response.json();
            state.paymentMethods = data;
            renderPaymentMethods();
        } catch (error) {
            console.error('Error fetching payment methods:', error);
        }
    }

    // --- CART LOGIC ---
    function addToCart(productId) {
        const existingItem = state.cart.find(item => item.id === productId);
        if (existingItem) {
            existingItem.quantity++;
        } else {
            const product = state.products.find(p => p.id === productId);
            if (product) {
                state.cart.push({
                    id: product.id,
                    name: product.name,
                    quantity: 1,
                    price_usd: parseFloat(product.price_usd),
                    original_price_usd: parseFloat(product.price_usd),
                    discount_percent: 0,
                });
            }
        }
        renderCart();
    }

    function updateCartItem(productId, newValues) {
        const item = state.cart.find(i => i.id === productId);
        if (!item) return;

        Object.assign(item, newValues);
        renderCart();
    }

    function handleQuantityChange(productId, newQuantity) {
        const quantity = parseFloat(newQuantity) || 0;
        updateCartItem(productId, { quantity });
    }

    function handlePriceChange(productId, newPrice) {
        const price_usd = parseFloat(newPrice) || 0;
        const item = state.cart.find(i => i.id === productId);
        if (!item) return;

        const discount_percent = ((item.original_price_usd - price_usd) / item.original_price_usd) * 100;
        updateCartItem(productId, { price_usd, discount_percent: discount_percent });
    }

    function handleDiscountChange(productId, newDiscount) {
        const discount_percent = parseFloat(newDiscount) || 0;
        const item = state.cart.find(i => i.id === productId);
        if (!item) return;

        const price_usd = item.original_price_usd * (1 - (discount_percent / 100));
        updateCartItem(productId, { price_usd, discount_percent });
    }

    function handleRemoveItem(productId) {
        state.cart = state.cart.filter(item => item.id !== productId);
        renderCart();
    }

    // --- RENDER & CALCULATION ---
    function renderCart() {
        orderlinesBodyEl.innerHTML = '';
        if (state.cart.length === 0) {
            orderlinesBodyEl.innerHTML = '<div class="orderline empty">No products in order</div>';
        }

        state.cart.forEach(item => {
            const totalUsd = item.quantity * item.price_usd;
            const priceVes = item.price_usd * state.exchangeRate;
            const orderLine = document.createElement('div');
            orderLine.className = 'orderline';
            orderLine.innerHTML = `
                <div class="col-product">${item.name}</div>
                <div class="col-qty"><input type="number" class="line-input" value="${item.quantity}" data-id="${item.id}" data-type="qty"></div>
                <div class="col-price">
                    <input type="number" class="line-input" value="${item.price_usd.toFixed(2)}" data-id="${item.id}" data-type="price">
                    <span class="price-ves">Bs. ${priceVes.toFixed(2)}</span>
                </div>
                <div class="col-discount"><input type="number" class="line-input" value="${item.discount_percent.toFixed(0)}" data-id="${item.id}" data-type="discount"></div>
                <div class="col-total">
                    <span class="price-usd">$ ${totalUsd.toFixed(2)}</span>
                    <span class="price-ves">Bs. ${(totalUsd * state.exchangeRate).toFixed(2)}</span>
                </div>
                <div class="col-remove"><button class="btn-remove" data-id="${item.id}">&times;</button></div>
            `;
            orderlinesBodyEl.appendChild(orderLine);
        });

        calculateTotals();
    }

    function calculateTotals() {
        let totalUsd = 0;
        state.cart.forEach(item => {
            totalUsd += item.quantity * item.price_usd;
        });

        const totalVes = totalUsd * state.exchangeRate;

        totalUsdEl.textContent = `$ ${totalUsd.toFixed(2)}`;
        totalVesEl.textContent = `Bs. ${totalVes.toFixed(2)}`;
    }

    function renderProducts(productsToRender) {
        productListEl.innerHTML = '';
        productsToRender.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.addEventListener('click', () => addToCart(product.id));
            card.innerHTML = `
                <img src="${product.image_url || '/static/img/undraw_posting_photo.svg'}" alt="${product.name}">
                <div class="product-card-details"><h5>${product.name}</h5></div>
            `;
            productListEl.appendChild(card);
        });
    }

    function renderCategories(categoriesToRender) {
        categoryButtonsEl.innerHTML = '';
        const allButton = document.createElement('button');
        allButton.className = 'btn btn-info active';
        allButton.textContent = 'All';
        allButton.dataset.categoryId = '';
        allButton.addEventListener('click', () => handleCategoryFilterChange(''));
        categoryButtonsEl.appendChild(allButton);

        categoriesToRender.forEach(category => {
            const button = document.createElement('button');
            button.className = 'btn btn-info';
            button.textContent = category.name;
            button.dataset.categoryId = category.id;
            button.addEventListener('click', () => handleCategoryFilterChange(category.id));
            categoryButtonsEl.appendChild(button);
        });
    }

    function renderCustomers(customersToRender) {
        customerListEl.innerHTML = '';

        const deselectButton = document.createElement('a');
        deselectButton.href = '#';
        deselectButton.className = 'list-group-item list-group-item-action list-group-item-danger';
        deselectButton.textContent = 'Deselect Customer';
        deselectButton.addEventListener('click', (e) => {
            e.preventDefault();
            handleDeselectCustomer();
        });
        customerListEl.appendChild(deselectButton);

        customersToRender.forEach(customer => {
            const customerItem = document.createElement('a');
            customerItem.href = '#';
            customerItem.className = 'list-group-item list-group-item-action';
            customerItem.textContent = customer.text;
            customerItem.addEventListener('click', (e) => {
                e.preventDefault();
                handleCustomerSelect(customer);
            });
            customerListEl.appendChild(customerItem);
        });
    }

    function renderPaymentMethods() {
        paymentMethodsButtonsEl.innerHTML = '';
        state.paymentMethods.forEach(pm => {
            const button = document.createElement('button');
            button.className = 'btn btn-outline-secondary';
            button.textContent = pm.name;
            button.dataset.id = pm.id;
            button.addEventListener('click', () => handlePaymentMethodSelect(pm));
            paymentMethodsButtonsEl.appendChild(button);
        });
    }

    // --- EVENT HANDLERS ---
    function handleCategoryFilterChange(categoryId) {
        fetchProducts(searchInput.value, categoryId);
    }

    function handleCustomerSelect(customer) {
        state.selectedCustomer = customer;
        customerBtnText.textContent = customer.text;
        customerModal.hide();
    }

    function handleDeselectCustomer() {
        state.selectedCustomer = null;
        customerBtnText.textContent = 'Customer';
        customerModal.hide();
    }

    function handleAddNewCustomer() {
        customerModal.hide();
        newCustomerModal.show();
    }

    function handleSaveNewCustomer() {
        const customerData = {
            first_name: document.getElementById('new-customer-first-name').value,
            last_name: document.getElementById('new-customer-last-name').value,
            tax_id: document.getElementById('new-customer-tax-id').value,
            email: document.getElementById('new-customer-email').value,
            phone: document.getElementById('new-customer-phone').value,
            address: document.getElementById('new-customer-address').value,
        };
        createCustomer(customerData);
    }

    function openPaymentModal() {
        const totalUsd = state.cart.reduce((acc, item) => acc + item.quantity * item.price_usd, 0);
        paymentTotalUsdEl.textContent = `$ ${totalUsd.toFixed(2)}`;
        paymentTotalVesEl.textContent = `Bs. ${(totalUsd * state.exchangeRate).toFixed(2)}`;
        updatePaymentTotals();
    }

    function handlePaymentMethodSelect(paymentMethod) {
        // Prefill amount if it's the first payment
        if (state.currentPayments.length === 0) {
            const totalUsd = state.cart.reduce((acc, item) => acc + item.quantity * item.price_usd, 0);
            paymentAmountInput.value = totalUsd.toFixed(2);
        }
        if (paymentMethod.requires_reference) {
            paymentReferenceInput.style.display = 'block';
        } else {
            paymentReferenceInput.style.display = 'none';
        }
    }

    function handleAddPayment() {
        const amount = parseFloat(paymentAmountInput.value);
        const selectedPmEl = paymentMethodsButtonsEl.querySelector('.active');
        if (!selectedPmEl || !amount || amount <= 0) {
            alert('Please select a payment method and enter a valid amount.');
            return;
        }
        const paymentMethodId = parseInt(selectedPmEl.dataset.id);
        const paymentMethod = state.paymentMethods.find(pm => pm.id === paymentMethodId);
        const reference = paymentReferenceInput.value;

        if (paymentMethod.requires_reference && !reference) {
            alert('This payment method requires a reference.');
            return;
        }

        state.currentPayments.push({
            payment_method_id: paymentMethodId,
            payment_method_name: paymentMethod.name,
            amount: amount,
            reference: reference,
        });

        paymentAmountInput.value = '';
        paymentReferenceInput.value = '';
        updatePaymentTotals();
        renderPaymentLines();
    }

    function updatePaymentTotals() {
        const totalUsd = state.cart.reduce((acc, item) => acc + item.quantity * item.price_usd, 0);
        const paidAmount = state.currentPayments.reduce((acc, p) => acc + p.amount, 0);
        const remaining = totalUsd - paidAmount;
        const change = paidAmount > totalUsd ? paidAmount - totalUsd : 0;

        paymentRemainingUsdEl.textContent = `$ ${remaining > 0 ? remaining.toFixed(2) : '0.00'}`;
        paymentChangeUsdEl.textContent = `$ ${change.toFixed(2)}`;
    }

    function renderPaymentLines() {
        paymentLinesListEl.innerHTML = '';
        state.currentPayments.forEach((p, index) => {
            const line = document.createElement('li');
            line.className = 'list-group-item d-flex justify-content-between align-items-center';
            line.innerHTML = `
                <span>${p.payment_method_name}: $${p.amount.toFixed(2)} ${p.reference ? `(${p.reference})` : ''}</span>
                <button class="btn btn-danger btn-sm" data-index="${index}">&times;</button>
            `;
            paymentLinesListEl.appendChild(line);
        });
    }

    async function finalizeSale(isCredit = false) {
        if (!state.selectedCustomer) {
            alert('Please select a customer.');
            return;
        }

        const totalUsd = state.cart.reduce((acc, item) => acc + item.quantity * item.price_usd, 0);
        const paidAmount = state.currentPayments.reduce((acc, p) => acc + p.amount, 0);

        if (!isCredit && paidAmount < totalUsd) {
            alert('The paid amount is less than the total.');
            return;
        }

        const saleData = {
            customer: state.selectedCustomer.id,
            sub_total: totalUsd, // Assuming sub_total is the same as grand_total for now
            grand_total: totalUsd,
            tax_amount: 0, // Add tax calculation if needed
            tax_percentage: 0,
            amount_change: paidAmount > totalUsd ? paidAmount - totalUsd : 0,
            total_ves: totalUsd * state.exchangeRate,
            igtf_amount: 0, // Add IGTF calculation if needed
            is_credit: isCredit,
            products: state.cart.map(item => ({
                id: item.id,
                quantity: item.quantity,
                price: item.price_usd,
                total_product: item.quantity * item.price_usd,
            })),
            payments: state.currentPayments,
        };

        try {
            const response = await fetch(window.location.pathname, { // Post to the same URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(saleData),
            });

            const data = await response.json();

            if (data.status === 'success') {
                alert(data.message);
                resetPOS();
                paymentModal.hide();
            } else {
                alert(`Error: ${data.message}`);
            }
        } catch (error) {
            console.error('Error finalizing sale:', error);
            alert('An unexpected error occurred.');
        }
    }

    function resetPOS() {
        state.cart = [];
        state.currentPayments = [];
        state.selectedCustomer = null;
        customerBtnText.textContent = 'Customer';
        renderCart();
        renderPaymentLines();
        updatePaymentTotals();
    }

    function togglePanels() {
        state.isLeftPanelActive = !state.isLeftPanelActive;
        if (state.isLeftPanelActive) {
            leftPane.classList.add('is-active');
            rightPane.classList.add('is-hidden');
            if(switcherIcon) switcherIcon.className = 'fas fa-th-large'; // Icon for products view
        } else {
            leftPane.classList.remove('is-active');
            rightPane.classList.remove('is-hidden');
            if(switcherIcon) switcherIcon.className = 'fas fa-list-alt'; // Icon for order/cart view
        }
    }

    orderlinesBodyEl.addEventListener('change', function(e) {
        if (e.target.classList.contains('line-input')) {
            const productId = parseInt(e.target.dataset.id);
            const type = e.target.dataset.type;
            const value = e.target.value;

            if (type === 'qty') handleQuantityChange(productId, value);
            else if (type === 'price') handlePriceChange(productId, value);
            else if (type === 'discount') handleDiscountChange(productId, value);
        }
    });

    orderlinesBodyEl.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-remove')) {
            const productId = parseInt(e.target.dataset.id);
            handleRemoveItem(productId);
        }
    });

    searchInput.addEventListener('input', (e) => fetchProducts(e.target.value, ''));

    if (panelSwitcherBtn) {
        panelSwitcherBtn.addEventListener('click', togglePanels);
    }

    if (categoryDropdownEl) {
        categoryDropdownEl.addEventListener('change', (e) => handleCategoryFilterChange(e.target.value));
    }

    customerBtn.addEventListener('click', () => {
        customerModal.show();
        fetchCustomers();
    });

    customerSearchInput.addEventListener('input', (e) => fetchCustomers(e.target.value));

    addNewCustomerBtn.addEventListener('click', handleAddNewCustomer);

    saveNewCustomerBtn.addEventListener('click', handleSaveNewCustomer);

    paymentBtn.addEventListener('click', () => {
        paymentModal.show();
        openPaymentModal();
    });

    addPaymentBtn.addEventListener('click', handleAddPayment);

    finalizePaymentBtn.addEventListener('click', () => finalizeSale(false));

    creditSaleBtn.addEventListener('click', () => finalizeSale(true));

    paymentLinesListEl.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-danger')) {
            const index = parseInt(e.target.dataset.index);
            state.currentPayments.splice(index, 1);
            renderPaymentLines();
            updatePaymentTotals();
        }
    });

    // --- UTILS ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // --- INITIALIZATION ---
    function init() {
        state.exchangeRate = parseFloat(JSON.parse(document.getElementById('exchange_rate').textContent)) || 0;
        fetchProducts();
        fetchCategories();
        fetchPaymentMethods();
        renderCart();
    }

    init();
});