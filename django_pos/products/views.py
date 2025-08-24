from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Category, Product, InventoryMovement
from suppliers.models import Supplier
from authentication.decorators import admin_required

def generate_sku(category_prefix):
    # Get the last product in the category
    last_product = Product.objects.filter(category__prefix=category_prefix).order_by('-id').first()
    if last_product and last_product.sku:
        # Extract the number from the last SKU
        try:
            last_sku_number = int(last_product.sku[len(category_prefix):])
        except ValueError:
            last_sku_number = 0
        new_sku_number = last_sku_number + 1
    else:
        new_sku_number = 1
    # Format the SKU with leading zeros
    new_sku = f"{category_prefix}{new_sku_number:04d}"
    return new_sku

@admin_required
@login_required(login_url="/accounts/login/")
def categories_list_view(request):
    context = {
        "active_icon": "products_categories",
        "categories": Category.objects.all()
    }
    return render(request, "products/categories.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def categories_add_view(request):
    context = {
        "active_icon": "products_categories",
        "category_status": Category.status.field.choices
    }

    if request.method == 'POST':
        data = request.POST

        attributes = {
            "name": data['name'],
            "status": data['state'],
            "description": data['description']
        }

        if Category.objects.filter(**attributes).exists():
            messages.error(request, 'Category already exists!',
                           extra_tags="warning")
            return redirect('products:categories_add')

        try:
            new_category = Category.objects.create(**attributes)
            new_category.save()

            messages.success(request, 'Category: ' +
                             attributes["name"] + ' created successfully!', extra_tags="success")
            return redirect('products:categories_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the creation!', extra_tags="danger")
            print(e)
            return redirect('products:categories_add')

    return render(request, "products/categories_add.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def categories_update_view(request, category_id):
    """
    Args:
        request:
        category_id : The category's ID that will be updated
    """

    try:
        category = Category.objects.get(id=category_id)
    except Exception as e:
        messages.success(
            request, 'There was an error trying to get the category!', extra_tags="danger")
        print(e)
        return redirect('products:categories_list')

    context = {
        "active_icon": "products_categories",
        "category_status": Category.status.field.choices,
        "category": category
    }

    if request.method == 'POST':
        data = request.POST

        attributes = {
            "name": data['name'],
            "status": data['state'],
            "description": data['description']
        }

        if Category.objects.filter(**attributes).exists():
            messages.error(request, 'Category already exists!',
                           extra_tags="warning")
            return redirect('products:categories_add')

        try:
            category = Category.objects.filter(
                id=category_id).update(**attributes)

            category = Category.objects.get(id=category_id)

            messages.success(request, '¡Category: ' + category.name +
                             ' updated successfully!', extra_tags="success")
            return redirect('products:categories_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the elimination!', extra_tags="danger")
            print(e)
            return redirect('products:categories_list')

    return render(request, "products/categories_update.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def categories_delete_view(request, category_id):
    """
    Args:
        request:
        category_id : The category's ID that will be deleted
    """
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, '¡Category: ' + category.name +
                         ' deleted!', extra_tags="success")
        return redirect('products:categories_list')
    except Exception as e:
        messages.success(
            request, 'There was an error during the elimination!', extra_tags="danger")
        print(e)
        return redirect('products:categories_list')

@admin_required
@login_required(login_url="/accounts/login/")
def products_list_view(request):
    context = {
        "active_icon": "products",
        "products": Product.objects.all()
    }
    return render(request, "products/products.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def products_add_view(request):
    context = {
        "active_icon": "products_categories",
        "product_status": Product.status.field.choices,
        "categories": Category.objects.all().filter(status="ACTIVE"),
        "suppliers": Supplier.objects.all()
    }

    if request.method == 'POST':
        data = request.POST
        files = request.FILES # Get files from request

        attributes = {
            "name": data['name'],
            "status": data['status'],
            "description": data['description'],
            "category": Category.objects.get(id=data['category']),
            "supplier": Supplier.objects.get(id=data['supplier']),
            "price_usd": data['price_usd'],
            "stock": data['stock'],
            "stock_min": data['stock_min'],
            "applies_iva": 'applies_iva' in data, # Handle checkbox
        }

        # Generate SKU
        category = Category.objects.get(id=data['category'])
        attributes['sku'] = generate_sku(category.prefix)

        # Check if a product with the same name already exists
        if Product.objects.filter(name=attributes['name']).exists():
            messages.error(request, 'Product with this name already exists!',
                           extra_tags="danger")
            return redirect('products:products_add')

        try:
            new_product = Product(**attributes)

            if 'photo' in files:
                new_product.photo = files['photo']
            
            new_product.save()

            messages.success(request, 'Product: ' +
                             attributes["name"] + ' created successfully!', extra_tags="success")
            return redirect('products:products_list')
        except Exception as e:
            messages.error(
                request, f'There was an error during the creation! {e}', extra_tags="danger")
            print(e)
            return redirect('products:products_add')

    return render(request, "products/products_add.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def products_update_view(request, product_id):
    """
    Args:
        request:
        product_id : The product's ID that will be updated
    """

    try:
        product = Product.objects.get(id=product_id)
    except Exception as e:
        messages.success(
            request, 'There was an error trying to get the product!', extra_tags="danger")
        print(e)
        return redirect('products:products_list')

    context = {
        "active_icon": "products",
        "product_status": Product.status.field.choices,
        "product": product,
        "categories": Category.objects.all(),
        "suppliers": Supplier.objects.all()
    }

    if request.method == 'POST':
        data = request.POST
        files = request.FILES # Get files from request

        attributes = {
            "name": data['name'],
            "status": data['status'],
            "description": data['description'],
            "category": Category.objects.get(id=data['category']),
            "supplier": Supplier.objects.get(id=data['supplier']),
            "price_usd": data['price_usd'],
            "stock": data['stock'],
            "stock_min": data['stock_min'],
            "applies_iva": 'applies_iva' in data, # Handle checkbox
        }

        # Check if a product with the same name already exists (excluding the current product)
        if Product.objects.filter(name=attributes['name']).exclude(id=product_id).exists():
            messages.error(request, 'Product with this name already exists!',
                           extra_tags="danger")
            return redirect('products:products_update', product_id=product_id)

        try:
            product.name = attributes['name']
            product.status = attributes['status']
            product.description = attributes['description']
            product.category = attributes['category']
            product.supplier = attributes['supplier']
            product.price_usd = attributes['price_usd']
            product.stock = attributes['stock']
            product.stock_min = attributes['stock_min']
            product.applies_iva = attributes['applies_iva']

            if 'photo' in files:
                product.photo = files['photo']
            
            product.save()

            messages.success(request, 'Product: ' + product.name +
                             ' updated successfully!', extra_tags="success")
            return redirect('products:products_list')
        except Exception as e:
            messages.error(
                request, f'There was an error during the update! {e}', extra_tags="danger")
            print(e)
            return redirect('products:products_list')

    return render(request, "products/products_update.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def products_delete_view(request, product_id):
    """
    Args:
        request:
        product_id : The product's ID that will be deleted
    """
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, '¡Product: ' + product.name +
                         ' deleted!', extra_tags="success")
        return redirect('products:products_list')
    except Exception as e:
        messages.success(
            request, 'There was an error during the elimination!', extra_tags="danger")
        print(e)
        return redirect('products:products_list')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url="/accounts/login/")
def get_products_ajax_view(request):
    if request.method == 'POST':
        if is_ajax(request=request):
            data = []

            products = Product.objects.filter(
                name__icontains=request.POST['term'])
            for product in products[0:10]:
                item = product.to_json()
                data.append(item)

            return JsonResponse(data, safe=False)