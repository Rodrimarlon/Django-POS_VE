document.addEventListener('DOMContentLoaded', function () {
    console.log("New POS JavaScript loaded!");

    // --- STATE ---
    let isLeftPanelActive = false;
    let products = [];
    let categories = [];
    let activeCategoryId = '';

    // --- DOM ELEMENTS ---
    const panelSwitcherBtn = document.getElementById('panel-switcher');
    const leftPane = document.querySelector('.left-pane');
    const rightPane = document.querySelector('.right-pane');
    const switcherIcon = panelSwitcherBtn ? panelSwitcherBtn.querySelector('i') : null;
    const productListEl = document.getElementById('product-list');
    const categoryButtonsEl = document.getElementById('category-buttons');
    const categoryDropdownEl = document.getElementById('category-dropdown');
    const searchInput = document.getElementById('product-search');

    // --- API FUNCTIONS ---
    async function fetchProducts(search = '', category = '') {
        try {
            const url = JSON.parse(document.getElementById('product_list_api_url').textContent);
            const response = await fetch(`${url}?search=${search}&category=${category}`);
            products = await response.json();
            renderProducts(products);
        } catch (error) {
            console.error('Error fetching products:', error);
        }
    }

    async function fetchCategories() {
        try {
            const response = await fetch('/products/api/categories/');
            categories = await response.json();
            renderCategories(categories);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    }

    // --- RENDER FUNCTIONS ---
    function renderProducts(productsToRender) {
        if (!productListEl) return;
        productListEl.innerHTML = '';
        if (productsToRender.length === 0) {
            productListEl.innerHTML = '<p>No products found.</p>';
            return;
        }
        productsToRender.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.dataset.productId = product.id;

            card.innerHTML = `
                <img src="${product.image_url || '/static/img/undraw_posting_photo.svg'}" alt="${product.name}">
                <div class="product-card-details">
                    <h5>${product.name}</h5>
                </div>
            `;

            card.addEventListener('click', () => {
                console.log(`Product clicked: ${product.name}`);
                // Placeholder: Add product to cart logic here
            });
            productListEl.appendChild(card);
        });
    }

    function renderCategories(categoriesToRender) {
        if (!categoryButtonsEl || !categoryDropdownEl) return;

        // Render buttons
        categoryButtonsEl.innerHTML = '';
        const allButton = document.createElement('button');
        allButton.className = 'btn btn-info active';
        allButton.textContent = 'All';
        allButton.dataset.categoryId = '';
        allButton.addEventListener('click', () => handleCategoryChange(''));
        categoryButtonsEl.appendChild(allButton);

        categoriesToRender.forEach(category => {
            const button = document.createElement('button');
            button.className = 'btn btn-info';
            button.textContent = category.name;
            button.dataset.categoryId = category.id;
            button.addEventListener('click', () => handleCategoryChange(category.id));
            categoryButtonsEl.appendChild(button);
        });

        // Render dropdown
        categoryDropdownEl.innerHTML = '';
        const allOption = document.createElement('option');
        allOption.value = '';
        allOption.textContent = 'All Categories';
        categoryDropdownEl.appendChild(allOption);

        categoriesToRender.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            categoryDropdownEl.appendChild(option);
        });
    }

    // --- EVENT HANDLERS ---
    function handleCategoryChange(categoryId) {
        activeCategoryId = categoryId;

        // Update active state for buttons
        const buttons = categoryButtonsEl.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.dataset.categoryId === activeCategoryId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Update dropdown value
        categoryDropdownEl.value = activeCategoryId;

        fetchProducts(searchInput.value, activeCategoryId);
    }

    function togglePanels() {
        isLeftPanelActive = !isLeftPanelActive;
        if (isLeftPanelActive) {
            leftPane.classList.add('is-active');
            rightPane.classList.add('is-hidden');
            if(switcherIcon) switcherIcon.className = 'fas fa-th-large'; // Icon for products view
        } else {
            leftPane.classList.remove('is-active');
            rightPane.classList.remove('is-hidden');
            if(switcherIcon) switcherIcon.className = 'fas fa-list-alt'; // Icon for order/cart view
        }
    }

    // --- EVENT LISTENERS ---
    if (panelSwitcherBtn) {
        panelSwitcherBtn.addEventListener('click', togglePanels);
    }

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            fetchProducts(e.target.value, activeCategoryId);
        });
    }

    if (categoryDropdownEl) {
        categoryDropdownEl.addEventListener('change', (e) => {
            handleCategoryChange(e.target.value);
        });
    }

    // --- INITIALIZATION ---
    function init() {
        console.log("Initializing POS...");
        if (switcherIcon) {
            switcherIcon.className = 'fas fa-list-alt';
        }
        fetchProducts();
        fetchCategories();
    }

    init();
});