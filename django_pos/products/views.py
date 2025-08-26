from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, F
from django.shortcuts import render
from .models import Product, InventoryMovement
from authentication.decorators import admin_required, role_required


@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def products_list_view(request):
    context = {
        "active_icon": "products",
        "products": Product.objects.all()
    }
    return render(request, "products/products.html", context=context)


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


@admin_required
@login_required(login_url="/accounts/login/")
def inventory_report_view(request):
    low_stock_products = Product.objects.filter(stock__lt=F('minimum_stock_level'))
    inventory_movements = InventoryMovement.objects.all().order_by('-date')  # Order by date descending

    context = {
        "active_icon": "reports",  # Assuming a reports icon
        "low_stock_products": low_stock_products,
        "inventory_movements": inventory_movements,
    }
    return render(request, "products/inventory_report.html", context)
