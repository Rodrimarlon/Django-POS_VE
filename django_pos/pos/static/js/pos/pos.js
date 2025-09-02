document.addEventListener('DOMContentLoaded', function () {
    console.log("Advanced POS JavaScript loaded!");

    // --- STATE ---
    const state = {
        products: [],
        cart: [],
        exchangeRate: 0,
        isLeftPanelActive: false,
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
    
    // --- EVENT HANDLERS ---
    function handleCategoryFilterChange(categoryId) {
        fetchProducts(searchInput.value, categoryId);
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

    // --- INITIALIZATION ---
    function init() {
        state.exchangeRate = parseFloat(JSON.parse(document.getElementById('exchange_rate').textContent)) || 0;
        fetchProducts();
        fetchCategories();
        renderCart();
    }

    init();
});
