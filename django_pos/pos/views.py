import json
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, FloatField, F
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from products.models import Product, Category, InventoryMovement
from sales.models import Sale, SaleDetail
from customers.models import Customer
from core.models import PaymentMethod, ExchangeRate, Company
from authentication.decorators import role_required

@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def index(request):
    today = timezone.now().date()

    year = today.year
    monthly_earnings = []

    # Calculate earnings per month
    for month in range(1, 13):
        earning = Sale.objects.filter(date_added__year=year, date_added__month=month).aggregate(
            total_variable=Coalesce(Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_variable')
        monthly_earnings.append(earning)

    # Calculate annual earnings
    annual_earnings = Sale.objects.filter(date_added__year=year).aggregate(total_variable=Coalesce(
        Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_variable')
    annual_earnings = format(annual_earnings, '.2f')

    # AVG per month
    avg_month = format(sum(monthly_earnings)/12, '.2f')

    # Top-selling products
    top_products = Product.objects.annotate(quantity_sum=Sum(
        'saledetail__quantity')).order_by('-quantity_sum')[:3]

    top_products_names = []
    top_products_quantity = []

    for p in top_products:
        top_products_names.append(p.name)
        top_products_quantity.append(p.quantity_sum)

    print(top_products_names)
    print(top_products_quantity)

    context = {
        "active_icon": "dashboard",
        "products": Product.objects.all().count(),
        "categories": Category.objects.all().count(),
        "annual_earnings": annual_earnings,
        "monthly_earnings": json.dumps(monthly_earnings),
        "avg_month": avg_month,
        "top_products_names": json.dumps(top_products_names),
        "top_products_names_list": top_products_names,
        "top_products_quantity": json.dumps(top_products_quantity),
    }
    return render(request, "pos/index.html", context)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def pos_view(request, sale_id=None):
    sale = None
    sale_details_json = "[]"
    if sale_id:
        try:
            sale = Sale.objects.get(id=sale_id)
            # Prepare sale details for frontend
            sale_details = SaleDetail.objects.filter(sale=sale)
            sale_details_list = []
            for detail in sale_details:
                sale_details_list.append({
                    'id': detail.product.id,
                    'name': detail.product.name,
                    'price': str(detail.price),  # Convert Decimal to string
                    'quantity': detail.quantity,
                    'total_product': str(detail.total_detail),  # Convert Decimal to string
                    'sku': detail.product.sku,
                })
            sale_details_json = json.dumps(sale_details_list)

        except Sale.DoesNotExist:
            messages.error(request, 'Sale not found!', extra_tags="danger")
            return redirect('pos:pos')  # Redirect to new sale if not found

    # Fetch IGTF percentage from Company model
    igtf_percentage = 0.00
    try:
        company = Company.objects.first() # Assuming there's only one company or you want the first one
        if company:
            igtf_percentage = float(company.igtf_percentage)
    except Company.DoesNotExist:
        pass # Handle case where no company is configured

    # Fetch latest exchange rate
    exchange_rate = 0
    try:
        latest_rate = ExchangeRate.objects.latest('date')
        exchange_rate = latest_rate.rate_usd_ves
    except ExchangeRate.DoesNotExist:
        pass # Handle case where no exchange rate is configured

    context = {
        "active_icon": "pos",
        "sale": sale,
        "sale_details_json": sale_details_json,
        "igtf_percentage": igtf_percentage, # Pass IGTF percentage to context
        "product_list_api_url": reverse('products:product_list_api'),
        "categories_list_api_url": reverse('products:category_list_api'),
        "get_customers_api_url": reverse('customers:get_customers_api'),
        "create_customer_api_url": reverse('customers:create_customer_api'),
        "exchange_rate": exchange_rate,
        "clean_view": True,
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            try:
                data = json.load(request)

                sale_attributes = {
                    "customer": Customer.objects.get(id=int(data['customer'])),
                    "sub_total": float(data["sub_total"]),
                    "grand_total": float(data["grand_total"]),
                    "tax_amount": float(data["tax_amount"]),
                    "tax_percentage": float(data["tax_percentage"]),
                    "amount_payed": float(data["amount_payed"]),
                    "amount_change": float(data["amount_change"]),
                    "user": request.user,  # Assign current user
                    "total_ves": float(data.get("total_ves", 0)),  # New field
                    "igtf_amount": float(data.get("igtf_amount", 0)),  # New field
                    "is_credit": data.get("is_credit", False),  # New field
                    "payment_method": PaymentMethod.objects.get(id=int(data['payment_method'])) if 'payment_method' in data and data['payment_method'] else None,  # New field, handle empty string
                    "exchange_rate": ExchangeRate.objects.get(id=int(data['exchange_rate'])) if 'exchange_rate' in data and data['exchange_rate'] else None,  # New field, handle empty string
                }

                # Determine sale status
                action_type = data.get("action_type", "finalize")  # 'finalize' or 'draft'
                sale_attributes["status"] = 'draft' if action_type == 'draft' else 'completed'

                if sale_id:  # Update existing sale
                    Sale.objects.filter(id=sale_id).update(**sale_attributes)
                    current_sale = Sale.objects.get(id=sale_id)
                    SaleDetail.objects.filter(sale=current_sale).delete()  # Clear old details
                    message = 'Sale updated successfully!'
                else:  # Create new sale
                    current_sale = Sale.objects.create(**sale_attributes)
                    message = 'Sale created successfully!'

                products = data["products"]
                for product_data in products:
                    detail_attributes = {
                        "sale": current_sale,
                        "product": Product.objects.get(id=int(product_data["id"])),
                        "price": product_data["price"],
                        "quantity": product_data["quantity"],
                        "total_detail": product_data["total_product"]
                    }
                    SaleDetail.objects.create(**detail_attributes)

                # Stock deduction and InventoryMovement only on finalization
                if current_sale.status == 'completed':
                    for product_data in products:
                        product_obj = Product.objects.get(id=int(product_data["id"]))
                        product_obj.stock -= product_data["quantity"]
                        product_obj.save()

                        InventoryMovement.objects.create(
                            product=product_obj,
                            movement_type='out',
                            quantity=product_data["quantity"],
                            user=request.user,
                            reason=f'Sale {current_sale.id}'
                        )
                    message = 'Sale finalized and stock updated successfully!'
                elif current_sale.status == 'draft':
                    message = 'Sale saved as draft!'
                
                return JsonResponse({'status': 'success', 'message': message})

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        return redirect('sales:sales_list')  # Redirect to sales list after operation

    return render(request, "pos/pos.html", context=context)
