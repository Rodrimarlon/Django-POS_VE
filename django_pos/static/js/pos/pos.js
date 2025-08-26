    // Source: https://stackoverflow.com/a/32605063
    function roundTo(n, digits) {
        if (digits === undefined) {
            digits = 0;
        }

        var multiplicator = Math.pow(10, digits);
        n = parseFloat((n * multiplicator).toFixed(11));
        return Math.round(n) / multiplicator;
    }

    //Variable for product number in table
    var number = 1;

    //Variable to store sale details and products
    var sale = {
        items: {
            customer : 0, 
            sub_total : 0.00, 
            grand_total : 0.00, 
            tax_amount : 0.00, 
            tax_percentage : 0.00, 
            amount_payed : 0.00, 
            amount_change : 0.00,
            total_ves: 0.00, // New
            igtf_amount: 0.00, // New
            is_credit: false, // New
            payment_method: null, // New
            exchange_rate: null, // New
            action_type: 'finalize', // New: 'finalize' or 'draft'
            products: [

            ]
        },
        calculate_sale: function (){
            // Subtotal of all products added
            var sub_total = 0.00

            var tax_percentage = $('input[name="tax_percentage"]').val();

            // Calculates the total for each product
            $.each(this.items.products, function(pos, dict){
                dict.pos = pos;  
                dict.total_product = roundTo(dict.quantity * dict.price, 2);
                // Add the product total to the sale subtotal
                sub_total += roundTo(dict.total_product, 2);
            });

            //Update the sale subtotal, grand total, and tax amount
            this.items.sub_total = roundTo(sub_total, 2);
            this.items.grand_total = roundTo(this.items.sub_total, 2);
            this.items.tax_amount = roundTo(this.items.sub_total * (tax_percentage / 100), 2);
    
            $('input[name="sub_total"]').val(this.items.sub_total);
            $('input[name="tax_amount"]').val(this.items.tax_amount);
            $('input[name="grand_total"]').val(this.items.grand_total);

            // Calculate amount change
            this.items.amount_change = roundTo($('input[name="amount_payed"]').val() - this.items.grand_total, 2);
            $('input[name="amount_change"]').val(this.items.amount_change);

            // Calculate total_ves and igtf_amount
            var current_exchange_rate = parseFloat($('input[name="exchange_rate"]').val() || 0);
            this.items.total_ves = roundTo(this.items.grand_total * current_exchange_rate, 2);
            $('input[name="total_ves"]').val(this.items.total_ves);

            var selected_payment_method_id = $('#payment_method').val();
            var is_foreign_currency = false;
            // Assuming payment_methods_data is available globally or fetched
            if (payment_methods_data) {
                var pm = payment_methods_data.find(p => p.id == selected_payment_method_id);
                if (pm) {
                    is_foreign_currency = pm.is_foreign_currency;
                }
            }
            // Fetch IGTF percentage from hidden input
            var igtf_percentage_from_backend = parseFloat($('#igtf_percentage_from_backend').val() || 0) / 100;
            this.items.igtf_amount = is_foreign_currency ? roundTo(this.items.grand_total * igtf_percentage_from_backend, 2) : 0.00;
            $('input[name="igtf_amount"]').val(this.items.igtf_amount);
        },
        // Adds a product to the sale object
        add_product: function (item) {
            this.items.products.push(item);
            this.list_product();
        },
        // Shows the selected product in the table
        list_product: function () {
            // Calculate the sale 
            this.calculate_sale();

            tblProducts = $("#table_products").DataTable({
                destroy: true,
                data: this.items.products,
                columns: [
                    {"data": "number"}, 
                    {"data": "name"},
                    {"data": "price"},
                    {"data": "quantity"},
                    {"data": "total_product"},
                    {"data": "id"},
                ],
                columnDefs: [
                    {
                        // Quantity
                        class: 'text-center',
                        targets: [3], 
                        render: function (data, type, row){
                            return '<input name="quantity" type="text" class="form-control form-control-xs text-center input-sm" autocomplete="off" value="'+row.quantity+'">';
                        },                      
                    },
                    {
                        //Product price an total
                        class: 'text-right',
                        targets: [2,4],
                        render: function (data, type, row){
                            return parseFloat(data).toFixed(2) + ' $';
                        }
                    },
                    {
                        //Delete button
                        class: 'text-center',
                        targets: [-1],
                        orderable: false,
                        render: function (data, type, row){
                            return '<a rel="delete" type="button" class="btn btn-sm btn-danger" data-bs-toggle="tooltip" title="{% trans "Delete product" %}"> <i class="fas fa-trash-alt fa-xs"></i> </a>';
                        },
                    },

                ],
                rowCallback(row, data, displayNun, displayIndex, dataIndex){
                    $(row).find(("input[name='quantity']")).TouchSpin({
                        min: 1,
                        max: 100, //Máximo de acuerdo al stock de cada producto
                        step: 1,
                        decimals: 0,
                        boostat: 1,
                        maxboostedstep: 3,
                        postfix: ''
                    });
                },
            })
            
            // IDs de productos ya seleccionados para exlcuir en la busqueda
            //console.log("this.traer_ids()");
            //console.log(this.traer_ids());
            
        },
    };

    // Global variable to store payment methods data
    var payment_methods_data = [];

    $(document).ready(function() {
        // Fetch payment methods and populate dropdown
        $.ajax({
            url: "{% url 'core:payment_method_list' %}", // Assuming an API endpoint for payment methods
            type: "GET",
            dataType: "json",
            success: function(data) {
                payment_methods_data = data.payment_methods; // Store globally
                var select = $('#payment_method');
                $.each(payment_methods_data, function(index, pm) {
                    select.append($('<option>', {
                        value: pm.id,
                        text: pm.name
                    }));
                });
            },
            error: function(error) {
                console.error("Error fetching payment methods:", error);
            }
        });

        // Fetch current exchange rate
        $.ajax({
            url: "{% url 'core:exchange_rate_modal' %}", // Assuming this endpoint provides the current rate
            type: "GET",
            dataType: "json",
            success: function(data) {
                if (data.exchange_rate_exists) { // Assuming this indicates a rate is available
                    $('input[name="exchange_rate"]').val(data.rate_usd_ves); // Assuming rate is in data.rate_usd_ves
                    sale.calculate_sale(); // Recalculate with new rate
                } else {
                    Swal.fire({
                        title: '{% trans "No exchange rate for today!" %}',
                        text: '{% trans "Please set the daily exchange rate." %}',
                        icon: 'warning',
                        showCancelButton: false,
                        confirmButtonText: '{% trans "OK" %}',
                    });
                }
            },
            error: function(error) {
                console.error("Error fetching exchange rate:", error);
            }
        });

        // Pre-populate form if loading a draft sale
        var sale_data_element = document.getElementById('sale_data');
        var sale_obj = sale_data_element ? JSON.parse(sale_data_element.textContent) : null;

        var sale_details_data_element = document.getElementById('sale_details_data');
        var sale_details_obj = sale_details_data_element ? JSON.parse(sale_details_data_element.textContent) : [];

        if (sale_obj) { // Check if sale_obj is not null
            // Populate customer
            $('#searchbox_customers').val(sale_obj.customer).trigger('change');

            // Populate products
            sale.items.products = sale_details_obj;
            sale.list_product();

            // Populate other fields
            $('input[name="sub_total"]').val(sale_obj.sub_total);
            $('input[name="grand_total"]').val(sale_obj.grand_total);
            $('input[name="tax_amount"]').val(sale_obj.tax_amount);
            $('input[name="tax_percentage"]').val(sale_obj.tax_percentage);
            $('input[name="amount_payed"]').val(sale_obj.amount_payed);
            $('input[name="amount_change"]').val(sale_obj.amount_change);
            $('input[name="total_ves"]').val(sale_obj.total_ves);
            $('input[name="igtf_amount"]').val(sale_obj.igtf_amount);
            $('#is_credit').prop('checked', sale_obj.is_credit);
            $('#payment_method').val(sale_obj.payment_method).trigger('change');
            $('input[name="exchange_rate"]').val(sale_obj.exchange_rate); // Assuming exchange_rate is a direct value here
        }


        //Tax percentage touchspin
        $("input[name='tax_percentage']").TouchSpin({
            min: 0,
            max: 100,
            step: 1,
            decimals: 2,
            boostat: 5,
            maxboostedstep: 10,
            postfix: '%'
        }).on('change', function(){
            sale.calculate_sale();
        });

        // Amount payed change event
        $('input[name="amount_payed"]').on('change keyup', function() {
            sale.calculate_sale();
        });

        // Payment method change event
        $('#payment_method').on('change', function() {
            sale.items.payment_method = $(this).val();
            sale.calculate_sale();
        });

        // Is credit checkbox change event
        $('#is_credit').on('change', function() {
            sale.items.is_credit = $(this).is(':checked');
        });


        //Select2 customers
        console.log("Initializing customer Select2...");
        $('#searchbox_customers').select2({
            delay: 250,
            placeholder: "{% trans "Select a customer" %}",
            minimumInputLength: 1,
            allowClear: true,
            ajax: {
                url: "{% url 'customers:get_customers' %}",
                type: 'POST',
                data: function (params) {
                    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val(); // Get token here
                    var queryParameters = {
                        term: params.term,
                        csrfmiddlewaretoken: csrftoken // Explicitly include CSRF token
                    }
                    console.log("Customer search params:", queryParameters);
                    return queryParameters; // Let jQuery handle serialization
                },
                processResults: function (data) {
                    console.log("Customer search results:", data);
                    return {
                        results: data
                    };
                },
            }
        }).on('select2:select', function (e) {
            var data = e.params.data;
            console.log("Selected customer:", data);
        });
        console.log("Customer Select2 initialized.");

        // Tables Events
        $('#table_products tbody').on('click', 'a[rel="delete"]', function () {
                // When a product is deleted
                
                // Row variable of the table
                var tr = tblProducts.cell($(this).closest('td, li')).index();
                product_name = (tblProducts.row(tr.row).data().name)

                Swal.fire({
                    customClass: {
                        confirmButton: 'ml-3 btn btn-danger',
                        cancelButton: 'btn btn-info'
                    },
                    buttonsStyling: false,
                    title: "{% trans "Are you sure you want to delete this product from the sale?" %}",
                    text: product_name,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: '{% trans "Delete" %}',
                    cancelButtonText: '{% trans "Cancel" %}',
                    reverseButtons: true,

                }).then((result) => {
                    // Si se confirma
                    if (result.isConfirmed) {
                        
                        // Delete the product
                        sale.items.products.splice(tr.row, 1);
                        //List the table again
                        sale.list_product();
                        Swal.fire('{% trans "The product was eliminated!" %}', '', 'success')
                    };
                })



            }).on('change keyup', 'input[name="quantity"]', function(){
                // When a product changes is quantity
                var quantity = parseInt($(this).val());
                //console.log(quantity);
                // Row variable of the table
                var tr = tblProducts.cell($(this).closest('td, li')).index();
                console.log(tr);
                //var data = tblProductos.row(tr.row).node();
                //console.log(data);
                // Update the product quantity in the sale object
                sale.items.products[tr.row].quantity = quantity;
                console.log(sale.items.products);
                // Calculate the sale with the new quantity
                sale.calculate_sale();
                // Find the row to update the product total
                $('td:eq(4)', tblProducts.row(tr.row).node()).html(sale.items.products[tr.row].total_product + ' $');
        });

        // Delete all products
        $('.deleteAll').on('click', function(){
            // If there are no products doesn't do anything
            if(sale.items.products.length === 0 ) return false;
            // Alert the user
            Swal.fire({
                customClass: {
                    confirmButton: 'ml-3 btn btn-danger',
                    cancelButton: 'btn btn-info'
                },
                buttonsStyling: false,
                title: "{% trans "Are you sure you want to delete all products from the sale?" %}",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: '{% trans "Delete all" %}',
                cancelButtonText: '{% trans "Cancel" %}',
                reverseButtons: true,

            }).then((result) => {
                // Si se confirma
                if (result.isConfirmed) {
                    // Borramos todos los productos del objeto de venta
                    sale.items.products = [];
                    // Calculamos de vuelta la factura
                    sale.list_product();
                    Swal.fire('{% trans "All products were eliminated!" %}', '', 'success')
                };
            })
        });

        //Select2 products searchbox
        

        console.log("Initializing product Select2...");
        $('#searchbox_products').select2({
            delay: 250,
            placeholder: '{% trans "Search a product" %}',
            minimumInputLength: 1,
            allowClear: true,
            templateResult: template_product_searchbox,
            ajax:{ 
                url: "{% url 'products:get_products' %}",
                type: 'POST',
                data: function (params) {
                    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val(); // Get token here
                    var queryParameters = {
                        term: params.term,
                        csrfmiddlewaretoken: csrftoken // Explicitly include CSRF token
                    }
                    console.log("Product search params:", queryParameters);
                    return queryParameters; // Let jQuery handle serialization
                },
                processResults: function (data) {
                    console.log("Product search results:", data);
                    return {
                        results: data
                    };
                },
            }}).on('select2:select', function (e) {
                //When a product is selected from the searchbox
                var data = e.params.data;
                console.log("Selected product:", data);
                //Add number, subtotal and quantity of the product to the dictionary
                data.number = number;
                number++; //Increase the product number in the table
                //data.sub_total = 0;
                data.quantity = 1;
                //Add the product to the sale object
                sale.add_product(data);
                console.log("Sale items");      
                console.log(sale.items);      
                //Clean the searchbox after the product is selected
                $(this).val('').trigger('change.select2');
            });
        console.log("Product Select2 initialized.");
    
            // Products datatable
            
            tblProducts = $('#table_products').DataTable({
                columnDefs: [
                    {
                        targets: [-1], // column index (start from 0)
                        orderable: false, // set orderable false for selected columns
                    }
                ],
            });
            

        });

        // Product searchbox templateResult
        function template_product_searchbox(repo) {
            if (repo.loading) {
                return repo.text;
            }
        
            var option = $(
                '<div class="wrapper container">'+
                ' <div class="row">'+
                    '<div class="col-lg-11 text-left shadow-sm">'+
                      '<p style="margin-bottom: 5px;">'+
                      '<b>' + gettext("Name:") + '</b> ' + repo.text + " | " + gettext("Category:") + " " + "<span class='btn-info px-2'>" + repo.category + '</span> <br>'+
                      '<b>' + gettext("Price:") + '</b> <span class="btn-success px-2">'+repo.price+' $. </span>'+
                      '</p>'+
                    '</div>'+
                  '</div>'+
                '</div>');
        
            return option;
        }

        // Send the sale via ajax
        
        $('#finalize_sale_btn').on('click', function (e) {
            e.preventDefault(); // Prevent default form submission
            sale.items.action_type = 'finalize';
            submitSaleForm();
        });

        $('#save_draft_btn').on('click', function (e) {
            e.preventDefault(); // Prevent default form submission
            sale.items.action_type = 'draft';
            submitSaleForm();
        });

        function submitSaleForm() {
            // Only allow sending if we have at least one product
            if (sale.items.products.length === 0 ) {
                Swal.fire({
                    title: '{% trans "The sale must have at least 1 product" %}',
                    text: '{% trans "Search a product and add it to the sale" %}',
                    icon: 'warning',
                });
                return false;
            };
            
            // Only allow sending if the paid amount is equal or greater than the total for finalization
            if (sale.items.action_type === 'finalize' && $('[name="amount_payed"]').val() < $('[name="grand_total"]').val()) {
                Swal.fire({
                    title: '{% trans "Payable Amount is lower than the Grand Total" %}',
                    icon: 'warning',
                });
                return false;
            }

            // Agregamos los datos faltantes al objeto sales
            sale.items.customer = $('select[name="customer"]').val();
            sale.items.sub_total = $('input[name="sub_total"]').val(); 
            sale.items.grand_total = $('input[name="grand_total"]').val();
            sale.items.tax_amount = $('input[name="tax_amount"]').val(); 
            sale.items.tax_percentage = $('input[name="tax_percentage"]').val();
            sale.items.amount_payed = $('input[name="amount_payed"]').val(); 
            sale.items.amount_change = $('input[name="amount_change"]').val(); // Already calculated in calculate_sale

            sale.items.payment_method = $('#payment_method').val();
            sale.items.exchange_rate = $('input[name="exchange_rate"]').val();
            sale.items.is_credit = $('#is_credit').is(':checked');
            sale.items.total_ves = $('input[name="total_ves"]').val();
            sale.items.igtf_amount = $('input[name="igtf_amount"]').val();

            console.log("Sale:")
            console.log(sale.items)

            // Validate the csrf_token
            var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

            function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
            $.ajax({
                url: "{% if sale %}{% url 'pos:pos_add_with_id' sale.id %}{% else %}{% url 'pos:pos' %}{% endif %}",
                type: "POST",
                // We need to convert the JS object sale to string
                data: JSON.stringify(sale.items), 
                dataType: "json",
                processData: false,
                contentType: "application/json", // Set content type to JSON
                success: function (data) {
                    if (data.status === 'success') {
                        Swal.fire({
                            title: '{% trans "Success!" %}',
                            text: data.message,
                            icon: 'success',
                        }).then(() => {
                            window.location.href = "{% url 'sales:sales_list' %}";
                        });
                    } else {
                        Swal.fire({
                            title: '{% trans "Error!" %}',
                            text: data.message,
                            icon: 'error',
                        });
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    Swal.fire({
                        title: '{% trans "Error!" %}',
                        text: '{% trans "There was an error processing your request." %}' + ' (' + textStatus + ': ' + errorThrown + ')',
                        icon: 'error',
                    });
                },
            });
            
        } // End submitSaleForm

        // Attach submitSaleForm to form submission (for enter key, etc.)
        $('.saleForm').on('submit', function (e) {
            e.preventDefault(); // Prevent default form submission
            // If buttons are used, action_type is already set.
            // If form is submitted by enter key, default to finalize.
            if (!sale.items.action_type) {
                sale.items.action_type = 'finalize';
            }
            submitSaleForm();
        });
        
</script>
{% endblock javascripts %}
