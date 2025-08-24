import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_pos.wsgi import *
from django_pos import settings
from django.template.loader import get_template
from customers.models import Customer
from products.models import Product, InventoryMovement
from core.models import PaymentMethod, ExchangeRate
from weasyprint import HTML, CSS
from .models import Sale, SaleDetail
import json
from authentication.decorators import role_required, admin_required


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def sales_list_view(request):
    context = {
        "active_icon": "sales",
        "sales": Sale.objects.all()
    }
    return render(request, "sales/sales.html", context=context)

@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def sales_add_view(request, sale_id=None):
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
                    'price': str(detail.price), # Convert Decimal to string
                    'quantity': detail.quantity,
                    'total_product': str(detail.total_detail), # Convert Decimal to string
                    'sku': detail.product.sku,
                })
            sale_details_json = json.dumps(sale_details_list)

        except Sale.DoesNotExist:
            messages.error(request, 'Sale not found!', extra_tags="danger")
            return redirect('sales:sales_add') # Redirect to new sale if not found

    context = {
        "active_icon": "sales",
        "sale": sale,
        "sale_details_json": sale_details_json,
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            data = json.load(request)

            sale_attributes = {
                "customer": Customer.objects.get(id=int(data['customer'])),
                "sub_total": float(data["sub_total"]),
                "grand_total": float(data["grand_total"]),
                "tax_amount": float(data["tax_amount"]),
                "tax_percentage": float(data["tax_percentage"]),
                "amount_payed": float(data["amount_payed"]),
                "amount_change": float(data["amount_change"]),
                "user": request.user, # Assign current user
                "total_ves": float(data.get("total_ves", 0)), # New field
                "igtf_amount": float(data.get("igtf_amount", 0)), # New field
                "is_credit": data.get("is_credit", False), # New field
                "payment_method": PaymentMethod.objects.get(id=int(data['payment_method'])) if 'payment_method' in data and data['payment_method'] else None, # New field, handle empty string
                "exchange_rate": ExchangeRate.objects.get(id=int(data['exchange_rate'])) if 'exchange_rate' in data and data['exchange_rate'] else None, # New field, handle empty string
            }
            
            # Determine sale status
            action_type = data.get("action_type", "finalize") # 'finalize' or 'draft'
            sale_attributes["status"] = 'draft' if action_type == 'draft' else 'completed'

            try:
                if sale_id: # Update existing sale
                    Sale.objects.filter(id=sale_id).update(**sale_attributes)
                    current_sale = Sale.objects.get(id=sale_id)
                    SaleDetail.objects.filter(sale=current_sale).delete() # Clear old details
                    messages.success(request, 'Sale updated successfully!', extra_tags="success")
                else: # Create new sale
                    current_sale = Sale.objects.create(**sale_attributes)
                    messages.success(request, 'Sale created successfully!', extra_tags="success")
                
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
                    messages.success(request, 'Sale finalized and stock updated successfully!', extra_tags="success")
                elif current_sale.status == 'draft':
                    messages.success(request, 'Sale saved as draft!', extra_tags="success")

            except Exception as e:
                messages.error(
                    request, f'There was an error during the operation: {e}', extra_tags="danger")
                print(e) # For debugging

        return redirect('sales:sales_list') # Redirect to sales list after operation

    return render(request, "sales/sales_add.html", context=context)

@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def sales_details_view(request, sale_id):
    """
    Args:
        request:
        sale_id: ID of the sale to view
    """
    try:
        sale = Sale.objects.get(id=sale_id)

        details = SaleDetail.objects.filter(sale=sale)

        context = {
            "active_icon": "sales",
            "sale": sale,
            "details": details,
        }
        return render(request, "sales/sales_details.html", context=context)
    except Exception as e:
        messages.success(
            request, 'There was an error getting the sale!', extra_tags="danger")
        print(e)
        return redirect('sales:sales_list')

@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def receipt_pdf_view(request, sale_id):
    """
    Args:
        request:
        sale_id: ID of the sale to view the receipt
    """
    sale = Sale.objects.get(id=sale_id)

    details = SaleDetail.objects.filter(sale=sale)

    template = get_template("sales/sales_receipt_pdf.html")
    context = {
        "sale": sale,
        "details": details
    }
    html_template = template.render(context)

    css_url = os.path.join(
        settings.BASE_DIR, 'static/css/receipt_pdf/bootstrap.min.css')

    pdf = HTML(string=html_template).write_pdf(stylesheets=[CSS(css_url)])

    return HttpResponse(pdf, content_type="application/pdf")

@admin_required
@login_required(login_url="/accounts/login/")
def daily_cash_close_report_view(request):
    # Lógica para el reporte de cierre de caja diario
    # ...
    return render(request, "sales/daily_cash_close_report.html", {})

@admin_required
@login_required(login_url="/accounts/login/")
def pending_sales_list_view(request):
    pending_sales = Sale.objects.filter(is_credit=True, credit_paid=False)
    context = {
        "active_icon": "sales",
        "pending_sales": pending_sales
    }
    return render(request, "sales/pending_sales.html", context=context)