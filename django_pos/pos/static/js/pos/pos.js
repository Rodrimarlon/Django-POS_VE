const PosApp = {
    // --- STATE ---
    state: {
        products: [],
        cart: [],
        exchangeRate: 0,
        isLeftPanelActive: false,
        selectedCustomer: null,
        paymentMethods: [],
        currentPayments: [],
        loadedOrderId: null,
    },

    // --- DOM ELEMENTS ---
    dom: {
        productListEl: null,
        categoryButtonsEl: null,
        categoryDropdownEl: null,
        searchInput: null,
        orderlinesBodyEl: null,
        totalUsdEl: null,
        totalVesEl: null,
        panelSwitcherBtn: null,
        leftPane: null,
        rightPane: null,
        switcherIcon: null,
        customerBtn: null,
        customerBtnText: null,
        customerSearchInput: null,
        customerListEl: null,
        addNewCustomerBtn: null,
        saveNewCustomerBtn: null,
        newCustomerForm: null,
        paymentBtn: null,
        paymentTotalUsdEl: null,
        paymentTotalVesEl: null,
        paymentRemainingUsdEl: null,
        paymentMethodsButtonsEl: null,
        paymentAmountInput: null,
        paymentReferenceInput: null,
        addPaymentBtn: null,
        paymentLinesListEl: null,
        paymentChangeUsdEl: null,
        creditSaleBtn: null,
        finalizePaymentBtn: null,
        btnSaveOrder: null,
        ordersListContainerEl: null,
    },

    // --- INITIALIZATION ---
    init: function() {
        // Bind DOM elements
        this.dom.productListEl = document.getElementById('product-list');
        this.dom.categoryButtonsEl = document.getElementById('category-buttons');
        this.dom.categoryDropdownEl = document.getElementById('category-dropdown');
        this.dom.searchInput = document.getElementById('product-search');
        this.dom.orderlinesBodyEl = document.getElementById('orderlines-body');
        this.dom.totalUsdEl = document.getElementById('total-usd');
        this.dom.totalVesEl = document.getElementById('total-ves');
        this.dom.panelSwitcherBtn = document.getElementById('panel-switcher');
        this.dom.leftPane = document.querySelector('.left-pane');
        this.dom.rightPane = document.querySelector('.right-pane');
        this.dom.switcherIcon = this.dom.panelSwitcherBtn ? this.dom.panelSwitcherBtn.querySelector('i') : null;
        this.dom.customerBtn = document.getElementById('btn-customer');
        this.dom.customerBtnText = this.dom.customerBtn.querySelector('span');
        this.dom.customerSearchInput = document.getElementById('customer-search-input');
        this.dom.customerListEl = document.getElementById('customer-list');
        this.dom.addNewCustomerBtn = document.getElementById('add-new-customer-btn');
        this.dom.saveNewCustomerBtn = document.getElementById('save-new-customer-btn');
        this.dom.newCustomerForm = document.getElementById('new-customer-form');
        this.dom.paymentBtn = document.querySelector('.btn-payment');
        this.dom.paymentTotalUsdEl = document.getElementById('payment-total-usd');
        this.dom.paymentTotalVesEl = document.getElementById('payment-total-ves');
        this.dom.paymentRemainingUsdEl = document.getElementById('payment-remaining-usd');
        this.dom.paymentMethodsButtonsEl = document.getElementById('payment-methods-buttons');
        this.dom.paymentAmountInput = document.getElementById('payment-amount');
        this.dom.paymentReferenceInput = document.getElementById('payment-reference');
        this.dom.addPaymentBtn = document.getElementById('add-payment-btn');
        this.dom.paymentLinesListEl = document.getElementById('payment-lines-list');
        this.dom.paymentChangeUsdEl = document.getElementById('payment-change-usd');
        this.dom.creditSaleBtn = document.getElementById('credit-sale-btn');
        this.dom.finalizePaymentBtn = document.getElementById('finalize-payment-btn');
        this.dom.btnSaveOrder = document.getElementById('btn-save-order');
        this.dom.ordersListContainerEl = document.getElementById('orders-list-container');

        // Set initial state
        this.state.exchangeRate = parseFloat(JSON.parse(document.getElementById('exchange_rate').textContent)) || 0;

        // Fetch initial data
        this.fetchProducts();
        this.fetchCategories();
        this.fetchPaymentMethods();

        // Initial render
        this.renderCart();
        this.updatePaymentButtonState();

        // Bind event listeners
        this.bindEvents();
    },

    // --- EVENT BINDING ---
    bindEvents: function() {
        this.dom.orderlinesBodyEl.addEventListener('change', (e) => {
            if (e.target.classList.contains('line-input')) {
                const productId = parseInt(e.target.dataset.id);
                const type = e.target.dataset.type;
                const value = e.target.value;

                if (type === 'qty') this.handleQuantityChange(productId, value);
                else if (type === 'price') this.handlePriceChange(productId, value);
                else if (type === 'discount') this.handleDiscountChange(productId, value);
            }
        });

        this.dom.orderlinesBodyEl.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-remove')) {
                const productId = parseInt(e.target.dataset.id);
                this.handleRemoveItem(productId);
            }
        });

        this.dom.searchInput.addEventListener('input', (e) => this.fetchProducts(e.target.value, ''));

        if (this.dom.panelSwitcherBtn) {
            this.dom.panelSwitcherBtn.addEventListener('click', () => this.togglePanels());
        }

        if (this.dom.categoryDropdownEl) {
            this.dom.categoryDropdownEl.addEventListener('change', (e) => this.handleCategoryFilterChange(e.target.value));
        }

        this.dom.customerBtn.addEventListener('click', () => {
            $('#customer-modal').modal('show');
            this.fetchCustomers();
        });

        this.dom.customerSearchInput.addEventListener('input', (e) => this.fetchCustomers(e.target.value));
        this.dom.addNewCustomerBtn.addEventListener('click', () => this.handleAddNewCustomer());
        this.dom.saveNewCustomerBtn.addEventListener('click', () => this.handleSaveNewCustomer());

        this.dom.paymentBtn.addEventListener('click', () => {
            if (!this.state.selectedCustomer) {
                alert('Please select a customer before proceeding to payment.');
                return;
            }
            $('#payment-modal').modal('show');
            this.openPaymentModal();
        });

        this.dom.addPaymentBtn.addEventListener('click', () => this.handleAddPayment());
        this.dom.finalizePaymentBtn.addEventListener('click', () => this.finalizeSale(false));
        this.dom.creditSaleBtn.addEventListener('click', () => this.finalizeSale(true));

        if (this.dom.btnSaveOrder) {
            this.dom.btnSaveOrder.addEventListener('click', () => this.saveOrder());
        }

        this.dom.paymentLinesListEl.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-danger')) {
                const index = parseInt(e.target.dataset.index);
                this.state.currentPayments.splice(index, 1);
                this.renderPaymentLines();
                this.updatePaymentTotals();
            }
        });

        // Use jQuery for Bootstrap 4 event binding
        $('#orders-modal').on('show.bs.modal', () => {
            this.fetchOrders();
        });

        // Use event delegation for order list container
        this.dom.ordersListContainerEl.addEventListener('click', (e) => {
            const deleteButton = e.target.closest('.btn-delete-order');
            const orderInfo = e.target.closest('.order-info');

            if (deleteButton) {
                e.stopPropagation();
                const orderId = deleteButton.dataset.orderId;
                this.deleteOrder(orderId);
            } else if (orderInfo) {
                const orderId = orderInfo.dataset.orderId;
                this.loadOrder(orderId);
            }
        });
    },

    // --- API FUNCTIONS ---
    fetchProducts: async function(search = '', category = '') {
        try {
            const url = JSON.parse(document.getElementById('product_list_api_url').textContent);
            const response = await fetch(`${url}?search=${search}&category=${category}`);
            const data = await response.json();
            this.state.products = data.products;
            this.renderProducts(this.state.products);
        } catch (error) {
            console.error('Error fetching products:', error);
        }
    },

    fetchCategories: async function() {
        try {
            const url = JSON.parse(document.getElementById('categories_list_api_url').textContent);
            const response = await fetch(url);
            const categories = await response.json();
            this.renderCategories(categories);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    },

    fetchCustomers: async function(search = '') {
        try {
            const url = JSON.parse(document.getElementById('get_customers_api_url').textContent);
            const response = await fetch(`${url}?search=${search}`);
            const customers = await response.json();
            this.renderCustomers(customers);
        } catch (error) {
            console.error('Error fetching customers:', error);
        }
    },

    createCustomer: async function(customerData) {
        try {
            const url = JSON.parse(document.getElementById('create_customer_api_url').textContent);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: JSON.stringify(customerData),
            });
            const data = await response.json();
            if (data.status === 'success') {
                this.handleCustomerSelect(data.customer);
                $('#new-customer-modal').modal('hide');
            } else {
                console.error('Error creating customer:', data.message);
            }
        } catch (error) {
            console.error('Error creating customer:', error);
        }
    },

    fetchPaymentMethods: async function() {
        try {
            const url = JSON.parse(document.getElementById('payment_methods_list_api_url').textContent);
            const response = await fetch(url);
            const data = await response.json();
            this.state.paymentMethods = data;
            this.renderPaymentMethods();
        } catch (error) {
            console.error('Error fetching payment methods:', error);
        }
    },

    saveOrder: async function() {
        if (!this.state.selectedCustomer) {
            Swal.fire('No Customer Selected', 'Please select a customer before saving an order.', 'warning');
            return;
        }
        if (this.state.cart.length === 0) {
            Swal.fire('Cart is Empty', 'Cannot save an empty order.', 'warning');
            return;
        }

        const orderData = {
            customer: this.state.selectedCustomer.id,
            products: this.state.cart.map(item => ({
                id: item.id,
                quantity: item.quantity,
                price: item.price_usd,
                discount_percent: item.discount_percent,
            })),
        };

        try {
            const url = JSON.parse(document.getElementById('save_order_url').textContent);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(orderData),
            });

            const data = await response.json();

            if (data.status === 'success') {
                Swal.fire({
                    title: 'Order Saved!',
                    text: data.message,
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                });
                this.resetPOS();
            } else {
                Swal.fire('Error', data.message, 'error');
            }
        } catch (error) {
            console.error('Error saving order:', error);
            Swal.fire('Unexpected Error', 'An unexpected error occurred.', 'error');
        }
    },

    fetchOrders: async function() {
        this.dom.ordersListContainerEl.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></div>';
        try {
            const urlElement = document.getElementById('order_list_api_url');
            if (!urlElement) {
                throw new Error('URL element #order_list_api_url not found!');
            }
            const url = JSON.parse(urlElement.textContent);
            
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const orders = await response.json();

            this.renderOrders(orders);
        } catch (error) {
            console.error('Error in fetchOrders:', error);
            this.dom.ordersListContainerEl.innerHTML = '<div class="alert alert-danger">Could not load orders. See console for details.</div>';
        }
    },

    deleteOrder: async function(orderId) {
        const result = await Swal.fire({
            title: 'Are you sure?',
            text: `You are about to delete Order #${orderId}. You won\'t be able to revert this!`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        });

        if (result.isConfirmed) {
            const url = `/orders/${orderId}/delete/`;
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    Swal.fire('Deleted!', data.message, 'success');
                    this.fetchOrders(); // Refresh the list
                } else {
                    Swal.fire('Error!', data.message || 'Could not delete the order.', 'error');
                }
            } catch (error) {
                console.error('Error deleting order:', error);
                Swal.fire('Request Failed!', 'An unexpected error occurred.', 'error');
            }
        }
    },

    loadOrder: async function(orderId) {
        const url = `/orders/${orderId}/detail/`;
        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.status === 'success') {
                this.resetPOS();
                if (data.customer) {
                    this.handleCustomerSelect(data.customer);
                }
                
                this.state.cart = data.products.map(p => ({
                    id: p.id,
                    name: p.name,
                    quantity: parseInt(p.quantity, 10),
                    price_usd: parseFloat(p.price_usd),
                    original_price_usd: parseFloat(p.original_price_usd),
                    discount_percent: parseFloat(p.discount_percent),
                    category_name: p.category_name,
                }));

                this.state.loadedOrderId = orderId;

                this.renderCart();
                $('#orders-modal').modal('hide');
            } else {
                Swal.fire('Error loading order', data.message, 'error');
            }
        } catch (error) {
            console.error('Error loading order:', error);
            Swal.fire('Request Failed!', 'An unexpected error occurred while loading the order.', 'error');
        }
    },

    // --- CART LOGIC ---
    addToCart: function(productId) {
        const existingItem = this.state.cart.find(item => item.id === productId);
        if (existingItem) {
            existingItem.quantity++;
        } else {
            const product = this.state.products.find(p => p.id === productId);
            if (product) {
                this.state.cart.push({
                    id: product.id,
                    name: product.name,
                    quantity: 1,
                    price_usd: parseFloat(product.price_usd),
                    original_price_usd: parseFloat(product.price_usd),
                    discount_percent: 0,
                    category_name: product.category_name,
                });
            }
        }
        this.renderCart();
    },

    updateCartItem: function(productId, newValues) {
        const item = this.state.cart.find(i => i.id === productId);
        if (!item) return;

        Object.assign(item, newValues);
        this.renderCart();
    },

    handleQuantityChange: function(productId, newQuantity) {
        const quantity = parseFloat(newQuantity) || 0;
        this.updateCartItem(productId, { quantity });
    },

    handlePriceChange: function(productId, newPrice) {
        const price_usd = parseFloat(newPrice) || 0;
        const item = this.state.cart.find(i => i.id === productId);
        if (!item) return;

        const discount_percent = ((item.original_price_usd - price_usd) / item.original_price_usd) * 100;
        this.updateCartItem(productId, { price_usd, discount_percent: discount_percent });
    },

    handleDiscountChange: function(productId, newDiscount) {
        const discount_percent = parseFloat(newDiscount) || 0;
        const item = this.state.cart.find(i => i.id === productId);
        if (!item) return;

        const price_usd = item.original_price_usd * (1 - (discount_percent / 100));
        this.updateCartItem(productId, { price_usd, discount_percent });
    },

    handleRemoveItem: function(productId) {
        this.state.cart = this.state.cart.filter(item => item.id !== productId);
        this.renderCart();
    },

    // --- RENDER & CALCULATION ---
    renderCart: function() {
        this.dom.orderlinesBodyEl.innerHTML = '';
        if (this.state.cart.length === 0) {
            this.dom.orderlinesBodyEl.innerHTML = '<div class="orderline empty">No products in order</div>';
        }

        this.state.cart.forEach(item => {
            const totalUsd = item.quantity * item.price_usd;
            const priceVes = item.price_usd * this.state.exchangeRate;
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
                    <span class="price-ves">Bs. ${(totalUsd * this.state.exchangeRate).toFixed(2)}</span>
                </div>
                <div class="col-remove"><button class="btn-remove" data-id="${item.id}">&times;</button></div>
            `;
            this.dom.orderlinesBodyEl.appendChild(orderLine);
        });

        this.calculateTotals();
    },

    calculateTotals: function() {
        let totalUsd = 0;
        this.state.cart.forEach(item => {
            totalUsd += item.quantity * item.price_usd;
        });

        const totalVes = totalUsd * this.state.exchangeRate;

        this.dom.totalUsdEl.textContent = `$ ${totalUsd.toFixed(2)}`;
        this.dom.totalVesEl.textContent = `Bs. ${totalVes.toFixed(2)}`;
        this.updatePaymentButtonState();
    },

    updatePaymentButtonState: function() {
        if (this.state.selectedCustomer && this.state.cart.length > 0) {
            this.dom.paymentBtn.classList.remove('disabled');
        } else {
            this.dom.paymentBtn.classList.add('disabled');
        }
    },

    renderProducts: function(productsToRender) {
        this.dom.productListEl.innerHTML = '';
        productsToRender.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.addEventListener('click', () => this.addToCart(product.id));
            card.innerHTML = `
                <img src="${product.image_url || '/static/img/undraw_posting_photo.svg'}" alt="${product.name}">
                <div class="product-card-details"><h5>${product.name}</h5></div>
            `;
            this.dom.productListEl.appendChild(card);
        });
    },

    renderCategories: function(categoriesToRender) {
        this.dom.categoryButtonsEl.innerHTML = '';
        const allButton = document.createElement('button');
        allButton.className = 'btn btn-info active';
        allButton.textContent = 'All';
        allButton.dataset.categoryId = '';
        allButton.addEventListener('click', () => this.handleCategoryFilterChange(''));
        this.dom.categoryButtonsEl.appendChild(allButton);

        categoriesToRender.forEach(category => {
            const button = document.createElement('button');
            button.className = 'btn btn-info';
            button.textContent = category.name;
            button.dataset.categoryId = category.id;
            button.addEventListener('click', () => this.handleCategoryFilterChange(category.id));
            this.dom.categoryButtonsEl.appendChild(button);
        });
    },

    renderCustomers: function(customersToRender) {
        this.dom.customerListEl.innerHTML = '';

        const deselectButton = document.createElement('a');
        deselectButton.href = '#';
        deselectButton.className = 'list-group-item list-group-item-action list-group-item-danger';
        deselectButton.textContent = 'Deselect Customer';
        deselectButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleDeselectCustomer();
        });
        this.dom.customerListEl.appendChild(deselectButton);

        customersToRender.forEach(customer => {
            const customerItem = document.createElement('a');
            customerItem.href = '#';
            customerItem.className = 'list-group-item list-group-item-action';
            customerItem.textContent = customer.text;
            customerItem.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleCustomerSelect(customer);
            });
            this.dom.customerListEl.appendChild(customerItem);
        });
    },

    renderPaymentMethods: function() {
        this.dom.paymentMethodsButtonsEl.innerHTML = '';
        this.state.paymentMethods.forEach(pm => {
            const button = document.createElement('button');
            button.className = 'btn btn-outline-secondary';
            button.textContent = pm.name;
            button.dataset.id = pm.id;
            button.addEventListener('click', () => this.handlePaymentMethodSelect(pm));
            this.dom.paymentMethodsButtonsEl.appendChild(button);
        });
    },

    renderCategorySummary: function() {
        const summaryEl = document.getElementById('payment-summary-by-category');
        summaryEl.innerHTML = '';

        const groupedByCategory = this.state.cart.reduce((acc, item) => {
            const categoryName = item.category_name || 'Uncategorized';
            if (!acc[categoryName]) {
                acc[categoryName] = {
                    totalUsd: 0,
                };
            }
            const itemTotalUsd = item.quantity * item.price_usd;
            acc[categoryName].totalUsd += itemTotalUsd;
            return acc;
        }, {});

        let tableHtml = `
            <table class="category-summary-table">
                <thead>
                    <tr>
                        <th>Categoria</th>
                        <th class="text-right">$
                        <th class="text-right">VES</th>
                    </tr>
                </thead>
                <tbody>
        `;

        for (const categoryName in groupedByCategory) {
            const categoryData = groupedByCategory[categoryName];
            const totalVes = categoryData.totalUsd * this.state.exchangeRate;
            tableHtml += `
                <tr>
                    <td>${categoryName}</td>
                    <td class="text-right">${categoryData.totalUsd.toFixed(2)}</td>
                    <td class="text-right text-primary">${totalVes.toFixed(2)}</td>
                </tr>
            `;
        }

        tableHtml += `
                </tbody>
            </table>
        `;

        summaryEl.innerHTML = tableHtml;
    },

    renderOrders: function(orders) {
        this.dom.ordersListContainerEl.innerHTML = '';

        if (!orders || orders.length === 0) {
            this.dom.ordersListContainerEl.innerHTML = '<div class="alert alert-info">No saved orders found.</div>';
            return;
        }

        orders.forEach(order => {
            const orderItem = document.createElement('a');
            orderItem.href = '#';
            orderItem.className = 'list-group-item list-group-item-action';
            
            const createdDate = new Date(order.created_at).toLocaleString();

            orderItem.innerHTML = `
                <div class="d-flex w-100 justify-content-between align-items-center">
                    <div class="order-info" style="flex-grow: 1; cursor: pointer;" data-order-id="${order.id}">
                        <h5 class="mb-1">Order #${order.id}</h5>
                        <p class="mb-1">Customer: <strong>${order.customer_name}</strong></p>
                        <small>Total: <strong>$${parseFloat(order.total).toFixed(2)}</strong></small>
                        <br>
                        <small class="text-muted">${createdDate}</small>
                    </div>
                    <button class="btn btn-danger btn-sm btn-delete-order" data-order-id="${order.id}" style="flex-shrink: 0;">&times;</button>
                </div>
            `;

            this.dom.ordersListContainerEl.appendChild(orderItem);
        });
    },

    // --- EVENT HANDLERS ---
    handleCategoryFilterChange: function(categoryId) {
        this.fetchProducts(this.dom.searchInput.value, categoryId);
    },

    handleCustomerSelect: function(customer) {
        this.state.selectedCustomer = customer;
        this.dom.customerBtnText.textContent = customer.text;
        if ($('#customer-modal').is(':visible')) {
            $('#customer-modal').modal('hide');
        }
        this.updatePaymentButtonState();
    },

    handleDeselectCustomer: function() {
        this.state.selectedCustomer = null;
        this.dom.customerBtnText.textContent = 'Customer';
        $('#customer-modal').modal('hide');
        this.updatePaymentButtonState();
    },

    handleAddNewCustomer: function() {
        $('#customer-modal').modal('hide');
        $('#new-customer-modal').modal('show');
    },

    handleSaveNewCustomer: function() {
        const customerData = {
            first_name: document.getElementById('new-customer-first-name').value,
            last_name: document.getElementById('new-customer-last-name').value,
            tax_id: document.getElementById('new-customer-tax-id').value,
            email: document.getElementById('new-customer-email').value,
            phone: document.getElementById('new-customer-phone').value,
            address: document.getElementById('new-customer-address').value,
        };
        this.createCustomer(customerData);
    },

    openPaymentModal: function() {
        this.renderCategorySummary();
        const totalUsd = this.state.cart.reduce((acc, item) => acc + item.quantity * item.price_usd, 0);
        this.dom.paymentTotalUsdEl.textContent = `$ ${totalUsd.toFixed(2)}`;
        this.dom.paymentTotalVesEl.textContent = `Bs. ${(totalUsd * this.state.exchangeRate).toFixed(2)}`;
        this.updatePaymentTotals();
    },

    handlePaymentMethodSelect: function(paymentMethod) {
        // Prefill amount if it's the first payment
        if (this.state.currentPayments.length === 0) {
            const totalUsd = this.state.cart.reduce((acc, item) => acc + item.quantity * item.price_usd, 0);
            this.dom.paymentAmountInput.value = totalUsd.toFixed(2);
        }
        if (paymentMethod.requires_reference) {
            this.dom.paymentReferenceInput.style.display = 'block';
        } else {
            this.dom.paymentReferenceInput.style.display = 'none';
        }
    },

    handleAddPayment: function() {
        const amount = parseFloat(this.dom.paymentAmountInput.value);
        const selectedPmEl = this.dom.paymentMethodsButtonsEl.querySelector('.active');
        if (!selectedPmEl || !amount || amount <= 0) {
            alert('Please select a payment method and enter a valid amount.');
            return;
        }
        const paymentMethodId = parseInt(selectedPmEl.dataset.id);
        const paymentMethod = this.state.paymentMethods.find(pm => pm.id === paymentMethodId);
        const reference = this.dom.paymentReferenceInput.value;

        if (paymentMethod.requires_reference && !reference) {
            alert('This payment method requires a reference.');
            return;
        }

        let amountInUsd = amount;
        if (!paymentMethod.is_foreign_currency) {
            amountInUsd = amount / this.state.exchangeRate;
        }

        this.state.currentPayments.push({
            payment_method_id: paymentMethodId,
            payment_method_name: paymentMethod.name,
            amount: amountInUsd,
            reference: reference,
        });

        this.dom.paymentAmountInput.value = '';
        this.dom.paymentReferenceInput.value = '';
        this.updatePaymentTotals();
        this.renderPaymentLines();
        selectedPmEl.classList.remove('active');
    },

    updatePaymentTotals: function() {
        const totalUsd = this.state.cart.reduce((acc, item) => acc + item.quantity * item.price_usd, 0);
        const paidAmount = this.state.currentPayments.reduce((acc, p) => acc + p.amount, 0);
        const remaining = totalUsd - paidAmount;
        const change = paidAmount > totalUsd ? paidAmount - totalUsd : 0;

        const totalVes = totalUsd * this.state.exchangeRate;
        const remainingVes = remaining * this.state.exchangeRate;
        const changeVes = change * this.state.exchangeRate;

        document.getElementById('payment-total-usd').textContent = totalUsd.toFixed(2);
        document.getElementById('payment-total-ves').textContent = totalVes.toFixed(2);
        document.getElementById('payment-remaining-usd').textContent = `${remaining > 0 ? remaining.toFixed(2) : '0.00'}`;
        document.getElementById('payment-remaining-ves').textContent = `${remainingVes > 0 ? remainingVes.toFixed(2) : '0.00'}`;
        document.getElementById('payment-change-usd').textContent = change.toFixed(2);
        document.getElementById('payment-change-ves').textContent = changeVes.toFixed(2);


        if (paidAmount >= totalUsd) {
            this.dom.finalizePaymentBtn.disabled = false;
        } else {
            this.dom.finalizePaymentBtn.disabled = true;
        }
    },

    renderPaymentLines: function() {
        this.dom.paymentLinesListEl.innerHTML = '';
        this.state.currentPayments.forEach((p, index) => {
            const line = document.createElement('li');
            line.className = 'list-group-item d-flex justify-content-between align-items-center';
            line.innerHTML = `
                <span>${p.payment_method_name}: ${p.amount.toFixed(2)} ${p.reference ? `(${p.reference})` : ''}</span>
                <button class="btn btn-danger btn-sm" data-index="${index}">&times;</button>
            `;
            this.dom.paymentLinesListEl.appendChild(line);
        });
    },

    finalizeSale: async function(isCredit = false) {
        if (!this.state.selectedCustomer) {
            alert('Please select a customer.');
            return;
        }

        const totalUsd = this.state.cart.reduce((acc, item) => acc + item.quantity * item.price_usd, 0);
        const paidAmount = this.state.currentPayments.reduce((acc, p) => acc + p.amount, 0);

        if (!isCredit && paidAmount < totalUsd) {
            alert('The paid amount is less than the total.');
            return;
        }

        const saleData = {
            customer: this.state.selectedCustomer.id,
            sub_total: totalUsd,
            grand_total: totalUsd,
            tax_amount: 0,
            tax_percentage: 0,
            amount_change: paidAmount > totalUsd ? paidAmount - totalUsd : 0,
            total_ves: totalUsd * this.state.exchangeRate,
            igtf_amount: 0,
            is_credit: isCredit,
            products: this.state.cart.map(item => ({
                id: item.id,
                quantity: item.quantity,
                price: item.price_usd,
                total_product: item.quantity * item.price_usd,
            })),
            payments: this.state.currentPayments,
            loaded_order_id: this.state.loadedOrderId,
        };

        try {
            const response = await fetch(window.location.pathname, { // Post to the same URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(saleData),
            });

            const data = await response.json();

            if (data.status === 'success') {
                Swal.fire({
                    title: 'Venta Realizada!',
                    text: data.message,
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                });
                this.resetPOS();
                $('#payment-modal').modal('hide');
            } else {
                Swal.fire({
                    title: 'Error',
                    text: data.message,
                    icon: 'error'
                });
            }
        } catch (error) {
            console.error('Error finalizing sale:', error);
            Swal.fire({
                title: 'Error Inesperado',
                text: 'Ocurrió un error inesperado.',
                icon: 'error'
            });
        }
    },

    resetPOS: function() {
        this.state.cart = [];
        this.state.currentPayments = [];
        this.state.selectedCustomer = null;
        this.state.loadedOrderId = null;
        this.dom.customerBtnText.textContent = 'Customer';
        this.renderCart();
        this.renderPaymentLines();
        this.updatePaymentTotals();
    },

    togglePanels: function() {
        this.state.isLeftPanelActive = !this.state.isLeftPanelActive;
        if (this.state.isLeftPanelActive) {
            this.dom.leftPane.classList.add('is-active');
            this.dom.rightPane.classList.add('is-hidden');
            if(this.dom.switcherIcon) this.dom.switcherIcon.className = 'fas fa-th-large'; // Icon for products view
        } else {
            this.dom.leftPane.classList.remove('is-active');
            this.dom.rightPane.classList.remove('is-hidden');
            if(this.dom.switcherIcon) this.dom.switcherIcon.className = 'fas fa-list-alt'; // Icon for order/cart view
        }
    },

    // --- UTILS ---
    getCookie: function(name) {
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
};

document.addEventListener('DOMContentLoaded', function () {
    PosApp.init();
});
