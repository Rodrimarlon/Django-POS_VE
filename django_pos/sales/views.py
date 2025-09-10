import os
from datetime import date # Added
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Sum, F # Added
from django.db.models.functions import Coalesce # Added
from django_pos import settings
from django.template.loader import get_template
from core.models import PaymentMethod # Added
from weasyprint import HTML, CSS
from .models import Sale, SaleDetail
from authentication.decorators import role_required, admin_required


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def sales_list_view(request):
    context = {
        "active_icon": "sales",
        "sales": Sale.objects.all().order_by('-date_added')
    }
    return render(request, "sales/sales.html", context=context)



    

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
    except Sale.DoesNotExist:
        messages.error(request, f"Sale with ID {sale_id} not found.", extra_tags="danger")
        return redirect('sales:sales_list')
    except Exception as e:
        messages.error(request, 'There was an error getting the sale!', extra_tags="danger")
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

from datetime import datetime, time

@admin_required
@login_required(login_url="/accounts/login/")
def daily_cash_close_report_view(request):
    today = date.today()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)

    sales_today = Sale.objects.filter(date_added__range=(start_of_day, end_of_day), status='completed')

    total_sales_usd = sales_today.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_sales_ves = sales_today.aggregate(Sum('total_ves'))['total_ves__sum'] or 0
    
    sales_by_payment_method = sales_today.values('payment_method__name').annotate(total=Sum('grand_total')).order_by('payment_method__name')

    credit_sales = sales_today.filter(is_credit=True)
    total_credit_sales = credit_sales.aggregate(Sum('grand_total'))['grand_total__sum'] or 0

    context = {
        'today': today,
        'total_sales_usd': total_sales_usd,
        'total_sales_ves': total_sales_ves,
        'sales_by_payment_method': sales_by_payment_method,
        'total_credit_sales': total_credit_sales,
        'sales_today': sales_today,
        'active_icon': 'sales'
    }
    return render(request, "sales/daily_cash_close_report.html", context)

@admin_required
@login_required(login_url="/accounts/login/")
def pending_sales_list_view(request):
    pending_sales = Sale.objects.filter(is_credit=True, credit_paid=False).order_by('-date_added')
    context = {
        "active_icon": "sales",
        "pending_sales": pending_sales
    }
    return render(request, "sales/pending_sales.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def pay_credit_sale_view(request, sale_id):
    try:
        sale = Sale.objects.get(id=sale_id)
        if request.method == 'POST':
            payment_method_id = request.POST.get('payment_method')
            reference = request.POST.get('reference')
            
            payment_method = PaymentMethod.objects.get(id=payment_method_id)
            
            # Create CreditPayment record
            CreditPayment.objects.create(
                sale=sale,
                amount_usd=sale.grand_total,
                amount_ves=sale.total_ves,
                exchange_rate=sale.exchange_rate,
                payment_method=payment_method,
                reference=reference
            )
            
            # Update sale status
            sale.credit_paid = True
            sale.status = 'completed'
            sale.save()
            
            messages.success(request, 'Credit sale paid successfully!', extra_tags='success')
            return redirect('sales:pending_sales_list')

        payment_methods = PaymentMethod.objects.all()
        context = {
            'sale': sale,
            'payment_methods': payment_methods
        }
        return render(request, 'sales/pay_credit_sale.html', context)
    except Sale.DoesNotExist:
        messages.error(request, 'Sale not found!', extra_tags='danger')
        return redirect('sales:pending_sales_list')
