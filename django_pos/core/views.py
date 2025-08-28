from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import PaymentMethod, Company, ExchangeRate
from .forms import PaymentMethodForm, CompanyForm
from django.utils import timezone
from authentication.decorators import admin_required, role_required
from django.db import IntegrityError

@admin_required
@login_required(login_url="/accounts/login/")
def company_view(request):
    company = Company.objects.first()
    context = {
        "active_icon": "company",
        "company": company,
    }
    return render(request, "core/company.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def company_update_view(request):
    # Use get_or_create to simplify logic for existing or new company
    company, created = Company.objects.get_or_create(pk=1)

    if request.method == 'POST':
        # Pass request.FILES to handle the logo upload
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company details updated successfully!', extra_tags="success")
            return redirect('core:company_view')
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = CompanyForm(instance=company)

    context = {
        "active_icon": "company",
        "form": form,
    }
    return render(request, "core/company_update.html", context=context)

@login_required(login_url="/accounts/login/")
def exchange_rate_modal_view(request):
    today = timezone.now().date()
    exchange_rate_exists = ExchangeRate.objects.filter(date=today).exists()

    if request.method == 'POST':
        rate = request.POST.get('rate_usd_ves')
        if rate:
            try:
                rate = float(rate)
                ExchangeRate.objects.create(
                    date=today,
                    rate_usd_ves=rate,
                    user=request.user
                )
                messages.success(request, 'Exchange rate saved successfully!', extra_tags="success")
                return redirect('pos:index') # Redirect to dashboard or wherever appropriate
            except ValueError:
                messages.error(request, 'Invalid rate value!', extra_tags="danger")
            except Exception as e:
                messages.error(request, f'Error saving exchange rate: {e}', extra_tags="danger")
        else:
            messages.error(request, 'Exchange rate is required!', extra_tags="danger")
        return redirect('pos:index') # Redirect back to dashboard if error

    context = {
        'exchange_rate_exists': exchange_rate_exists,
    }
    return render(request, 'core/exchange_rate_modal.html', context)

@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def exchange_rate_list_view(request):
    context = {
        "active_icon": "exchange_rates",
        "exchange_rates": ExchangeRate.objects.all().order_by('-date')
    }
    return render(request, "core/exchange_rates.html", context=context)

def get_latest_exchange_rate_api(request):
    try:
        latest_rate = ExchangeRate.objects.latest('date')
        data = {
            'rate_usd_ves': latest_rate.rate_usd_ves
        }
    except ExchangeRate.DoesNotExist:
        data = {
            'rate_usd_ves': 0 # Or some other default
        }
    return JsonResponse(data)

def payment_method_list_api(request):
    payment_methods = PaymentMethod.objects.all()
    data = [{
        'id': pm.id,
        'name': pm.name,
        'is_foreign_currency': pm.is_foreign_currency
    } for pm in payment_methods]
    return JsonResponse(data, safe=False)
