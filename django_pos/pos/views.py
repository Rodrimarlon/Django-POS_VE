import json
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, FloatField, F
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from products.models import Product, Category, InventoryMovement
from sales.models import Sale, SaleDetail, Payment
from customers.models import Customer
from core.models import PaymentMethod, ExchangeRate, Company
from authentication.decorators import role_required
from .models import Order, OrderDetail

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


def _process_sale_data(request, data, sale_id=None):
    """
    Helper function to process the business logic of creating or updating a sale.
    This function is designed to be called from within the main pos_view.
    """
    sale_attributes = {
        "customer": Customer.objects.get(id=int(data['customer'])),
        "sub_total": Decimal(data["sub_total"]),
        "grand_total": Decimal(data["grand_total"]),
        "tax_amount": Decimal(data["tax_amount"]),
        "tax_percentage": Decimal(data["tax_percentage"]),
        "amount_change": Decimal(data["amount_change"]),
        "user": request.user,
        "total_ves": Decimal(data.get("total_ves", 0)),
        "igtf_amount": Decimal(data.get("igtf_amount", 0)),
        "is_credit": data.get("is_credit", False),
        "exchange_rate": ExchangeRate.objects.latest('date'),
    }

    # Determine sale status
    action_type = data.get("action_type", "finalize")
    if sale_attributes["is_credit"]:
        sale_attributes["status"] = 'pending_credit'
    else:
        sale_attributes["status"] = 'completed'

    if sale_id:
        # Note: Updating customer balance for edited credit sales is not handled here.
        # This would require a more complex logic to calculate the difference.
        Sale.objects.filter(id=sale_id).update(**sale_attributes)
        current_sale = Sale.objects.get(id=sale_id)
        SaleDetail.objects.filter(sale=current_sale).delete()  # Clear old details
        Payment.objects.filter(sale=current_sale).delete() # Clear old payments
        message = 'Sale updated successfully!'
    else:
        current_sale = Sale.objects.create(**sale_attributes)
        # Update customer outstanding balance on new credit sale
        if current_sale.is_credit:
            customer = current_sale.customer
            customer.outstanding_balance = F('outstanding_balance') + current_sale.grand_total
            customer.save()
        message = 'Sale created successfully!'

    # Create Payment objects
    if not sale_attributes["is_credit"]:
        payments = data.get("payments", [])
        for payment_data in payments:
            Payment.objects.create(
                sale=current_sale,
                payment_method=PaymentMethod.objects.get(id=int(payment_data["payment_method_id"])),
                amount=Decimal(payment_data["amount"]),
                reference=payment_data.get("reference", "")
            )

    products = data["products"]
    for product_data in products:
        detail_attributes = {
            "sale": current_sale,
            "product": Product.objects.get(id=int(product_data["id"])),
            "price": Decimal(product_data["price"]),
            "quantity": product_data["quantity"],
            "total_detail": Decimal(product_data["total_product"])
        }
        SaleDetail.objects.create(**detail_attributes)

    # Stock deduction and InventoryMovement for completed or credit sales
    if current_sale.status in ['completed', 'pending_credit']:
        for product_data in products:
            product_obj = Product.objects.get(id=int(product_data["id"]))
            product_obj.stock = F('stock') - product_data["quantity"]
            product_obj.save()

            InventoryMovement.objects.create(
                product=product_obj,
                movement_type='out',
                quantity=product_data["quantity"],
                user=request.user,
                reason=f'Sale {current_sale.id}'
            )
        message = 'Sale finalized and stock updated successfully!'
    
    return message


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
        "payment_methods_list_api_url": reverse('core:payment_method_list_api'),
        "save_order_url": reverse('pos:save_order'),
        "exchange_rate": exchange_rate,
        "clean_view": True,
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            try:
                data = json.load(request)
                message = _process_sale_data(request, data, sale_id)
                return JsonResponse({'status': 'success', 'message': message})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        return redirect('sales:sales_list')  # Redirect to sales list after operation

    return render(request, "pos/pos.html", context=context)


@login_required
@require_POST
def save_order_view(request):
    if not is_ajax(request):
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    try:
        data = json.load(request)
        cart_products = data.get('products', [])
        customer_id = data.get('customer')

        if not cart_products:
            return JsonResponse({'status': 'error', 'message': 'Cannot save an empty order.'}, status=400)

        customer = Customer.objects.get(id=customer_id) if customer_id else None

        # Create the main Order
        new_order = Order.objects.create(
            user=request.user,
            customer=customer
        )

        # Create the OrderDetail items
        for product_data in cart_products:
            OrderDetail.objects.create(
                order=new_order,
                product=Product.objects.get(id=int(product_data["id"])),
                quantity=int(product_data["quantity"]),
                price_usd=Decimal(product_data["price"]),
                discount_percent=Decimal(product_data.get("discount_percent", 0))
            )
        
        return JsonResponse({'status': 'success', 'message': 'Order saved successfully!'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
