from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, InventoryMovement
from django.core.paginator import Paginator

from authentication.decorators import admin_required
from django.db import IntegrityError, models
from django.http import JsonResponse


@login_required(login_url="/accounts/login/")
def products_list_view(request):
    """
    View that returns a list of all products.
    The products can be filtered by category.
    """
    # The product and category management is now done in the admin panel.
    # This view will now be the "Inventory" view.
    context = {
        "active_icon": "products",
        "products": Product.objects.all()
    }
    return render(request, "products/products.html", context=context)


@login_required(login_url="/accounts/login/")
def inventory_report_view(request):
    """
    View to generate an inventory report.
    - Shows products with stock below the minimum.
    - Shows a history of inventory movements.
    """
    low_stock_products = Product.objects.filter(stock__lt=models.F('min_stock'))
    inventory_movements = InventoryMovement.objects.all().order_by('-created_at')

    context = {
        "active_icon": "reports", # Or a new icon for reports
        "low_stock_products": low_stock_products,
        "inventory_movements": inventory_movements,
    }
    return render(request, "products/inventory_report.html", context)


def product_list_api(request):
    product_list = Product.objects.select_related('category').all().order_by('name')

    if 'search' in request.GET:
        search_term = request.GET['search']
        product_list = product_list.filter(
            models.Q(name__icontains=search_term) |
            models.Q(sku__icontains=search_term) |
            models.Q(category__name__icontains=search_term)
        )

    if 'category' in request.GET:
        category_id = request.GET['category']
        if category_id.isdigit():
            product_list = product_list.filter(category_id=category_id)

    # Paginate the results
    paginator = Paginator(product_list, 30) # Show 30 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    data = [{
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'price_usd': product.price_usd,
        'stock': product.stock,
        'image_url': product.photo.url if product.photo else '',
        'category_name': product.category.name if product.category else 'Uncategorized'
    } for product in page_obj.object_list]

    return JsonResponse({
        'products': data,
        'has_next': page_obj.has_next()
    })

def category_list_api(request):
    categories = Category.objects.all().order_by('name')
    data = [{
        'id': category.id,
        'name': category.name,
    } for category in categories]
    return JsonResponse(data, safe=False)
