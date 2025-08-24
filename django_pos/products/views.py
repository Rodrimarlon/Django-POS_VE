from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q # Added for OR queries
from django.shortcuts import render, redirect
from .models import Category, Product, InventoryMovement
from suppliers.models import Supplier
from authentication.decorators import admin_required, role_required
from .forms import ProductForm # Import the new form
from django.db import IntegrityError # Import IntegrityError

@role_required(allowed_roles=['admin', 'cashier'])
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

@role_required(allowed_roles=['admin', 'cashier'])
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
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Product created successfully!', extra_tags="success")
                return redirect('products:products_list')
            except IntegrityError:
                messages.error(request, 'A product with that name or SKU already exists.', extra_tags="danger")
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = ProductForm()

    context = {
        "active_icon": "products",
        "form": form,
        "categories": Category.objects.all().filter(status="ACTIVE"), # Still needed for template context if not using form.fields.category.queryset
        "suppliers": Supplier.objects.all() # Still needed for template context if not using form.fields.supplier.queryset
    }
    return render(request, "products/products_add.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def products_update_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found!', extra_tags="danger")
        return redirect('products:products_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Product updated successfully!', extra_tags="success")
                return redirect('products:products_list')
            except IntegrityError:
                messages.error(request, 'A product with that name or SKU already exists.', extra_tags="danger")
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = ProductForm(instance=product)

    context = {
        "active_icon": "products",
        "form": form,
        "categories": Category.objects.all(), # Still needed for template context
        "suppliers": Supplier.objects.all() # Still needed for template context
    }
    return render(request, "products/products_update.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def products_delete_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, 'Product: ' + product.name + ' deleted!', extra_tags="success")
    except Product.DoesNotExist:
        messages.error(request, 'Product not found!', extra_tags="danger")
    except IntegrityError:
        messages.error(request, 'Cannot delete this product because it is linked to existing inventory movements or sales.', extra_tags="danger")
    except Exception as e:
        messages.error(request, f'Error deleting product: {e}', extra_tags="danger")
    return redirect('products:products_list')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url="/accounts/login/")
def get_products_ajax_view(request):
    if request.method == 'POST':
        if is_ajax(request=request):
            data = []

            term = request.POST['term']
            print(f"Product search term: {term}")

            products = Product.objects.filter(
                Q(name__icontains=term) | Q(sku__icontains=term)
            )
            print(f"Found products: {products.count()}")
            for product in products[0:10]:
                item = product.to_json()
                data.append(item)
            print(f"Returning data: {data}")

            return JsonResponse(data, safe=False)