import os
import json
from datetime import date, datetime, time
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django_pos import settings
from weasyprint import HTML, CSS

from authentication.decorators import role_required, admin_required
from core.models import PaymentMethod, Company, ExchangeRate
from .models import Sale, SaleDetail, CreditPayment


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
    try:
        sale = Sale.objects.get(id=sale_id)
        details = SaleDetail.objects.filter(sale=sale)
        payment_methods = PaymentMethod.objects.all()

        context = {
            "active_icon": "sales",
            "sale": sale,
            "details": details,
            "payment_methods": payment_methods,
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
    sale = Sale.objects.get(id=sale_id)
    details = SaleDetail.objects.filter(sale=sale)
    template = get_template("sales/sales_receipt_pdf.html")
    context = {
        "sale": sale,
        "details": details
    }
    html_template = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, 'static/css/receipt_pdf/bootstrap.min.css')
    pdf = HTML(string=html_template).write_pdf(stylesheets=[CSS(css_url)])
    return HttpResponse(pdf, content_type="application/pdf")


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
    pending_sales = Sale.objects.filter(is_credit=True, grand_total__gt=F('amount_paid')).order_by('-date_added')
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
    except Sale.DoesNotExist:
        messages.error(request, 'Sale not found!', extra_tags='danger')
        return redirect('sales:pending_sales_list')

    if request.method == 'POST':
        payments_json = request.POST.get('payments_json')
        if not payments_json:
            messages.error(request, 'No payment data provided.', extra_tags='danger')
            return redirect('sales:pay_credit_sale', sale_id=sale.id)

        try:
            payments = json.loads(payments_json)
            if not payments:
                messages.error(request, 'You must add at least one payment.', extra_tags='danger')
                return redirect('sales:pay_credit_sale', sale_id=sale.id)

            with transaction.atomic():
                total_paid_in_usd = Decimal(0)
                total_igtf = Decimal(0)
                exchange_rate_obj = ExchangeRate.objects.latest('date')
                rate = exchange_rate_obj.rate_usd_ves
                igtf_percentage = Company.objects.first().igtf_percentage

                for payment_data in payments:
                    amount = Decimal(payment_data['amount'])
                    is_foreign = payment_data['is_foreign']
                    payment_method = PaymentMethod.objects.get(id=payment_data['payment_method_id'])

                    amount_usd = Decimal(0)
                    amount_ves = Decimal(0)
                    igtf_for_payment = Decimal(0)

                    if is_foreign:
                        amount_usd = amount
                        amount_ves = amount * rate
                        igtf_for_payment = amount_usd * (igtf_percentage / 100)
                        total_igtf += igtf_for_payment
                    else:
                        amount_ves = amount
                        amount_usd = amount / rate if rate > 0 else 0
                    
                    total_paid_in_usd += amount_usd

                    CreditPayment.objects.create(
                        sale=sale,
                        amount_usd=amount_usd,
                        amount_ves=amount_ves,
                        igtf_amount=igtf_for_payment,
                        exchange_rate=exchange_rate_obj,
                        payment_method=payment_method,
                        reference=payment_data.get('reference', '')
                    )

                # Update Sale object
                sale.amount_paid += total_paid_in_usd
                sale.igtf_amount += total_igtf
                
                # Update Sale status
                # Note: The balance calculation should consider the IGTF
                if sale.get_balance() <= 0:
                    sale.status = 'completed'
                    sale.amount_paid = sale.grand_total + sale.igtf_amount
                else:
                    sale.status = 'partially_paid'
                sale.save()

                # Update Customer's outstanding balance
                customer = sale.customer
                customer.outstanding_balance -= (total_paid_in_usd + total_igtf)
                if customer.outstanding_balance < 0:
                    customer.outstanding_balance = 0
                customer.save()

            messages.success(request, f'Payment of ${total_paid_in_usd:.2f} (+ ${total_igtf:.2f} IGTF) registered successfully!', extra_tags='success')
            return redirect('sales:pending_sales_list')

        except Exception as e:
            messages.error(request, f'An error occurred: {e}', extra_tags='danger')
            return redirect('sales:pay_credit_sale', sale_id=sale.id)

    payment_methods = PaymentMethod.objects.all()
    credit_payments = CreditPayment.objects.filter(sale=sale).order_by('-payment_date')
    
    company = Company.objects.first()
    igtf_percentage = company.igtf_percentage if company else 0
    
    latest_rate = ExchangeRate.objects.latest('date')
    exchange_rate = latest_rate.rate_usd_ves if latest_rate else 0

    context = {
        'sale': sale,
        'payment_methods': payment_methods,
        'credit_payments': credit_payments,
        'igtf_percentage': igtf_percentage,
        'exchange_rate': exchange_rate,
        'active_icon': 'sales',
    }
    return render(request, 'sales/pay_credit_sale.html', context)