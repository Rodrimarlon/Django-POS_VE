from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import PaymentMethod, Company, ExchangeRate
from .forms import PaymentMethodForm, CompanyForm
from datetime import date
from authentication.decorators import admin_required, role_required
from django.db import IntegrityError

@admin_required
@login_required(login_url="/accounts/login/")
def payment_method_list_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': # Check if it's an AJAX request
        payment_methods = PaymentMethod.objects.all()
        data = []
        for pm in payment_methods:
            data.append({
                'id': pm.id,
                'name': pm.name,
                'is_foreign_currency': pm.is_foreign_currency,
                'requires_reference': pm.requires_reference
            })
        return JsonResponse({'payment_methods': data})
    else:
        context = {
            "active_icon": "payment_methods",
            "payment_methods": PaymentMethod.objects.all()
        }
        return render(request, "core/payment_methods.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def payment_method_add_view(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment method created successfully!', extra_tags="success")
            return redirect('core:payment_method_list')
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = PaymentMethodForm()

    context = {
        "active_icon": "payment_methods",
        "form": form
    }
    return render(request, "core/payment_methods_add.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def payment_method_update_view(request, payment_method_id):
    try:
        payment_method = PaymentMethod.objects.get(id=payment_method_id)
    except PaymentMethod.DoesNotExist:
        messages.error(request, 'Payment method not found!', extra_tags="danger")
        return redirect('core:payment_method_list')

    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment method updated successfully!', extra_tags="success")
            return redirect('core:payment_method_list')
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = PaymentMethodForm(instance=payment_method)

    context = {
        "active_icon": "payment_methods",
        "form": form,
    }
    return render(request, "core/payment_methods_update.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def payment_method_delete_view(request, payment_method_id):
    try:
        payment_method = PaymentMethod.objects.get(id=payment_method_id)
        payment_method.delete()
        messages.success(request, 'Payment method deleted successfully!', extra_tags="success")
    except PaymentMethod.DoesNotExist:
        messages.error(request, 'Payment method not found!', extra_tags="danger")
    except IntegrityError:
        messages.error(request, 'Cannot delete this payment method because it is linked to existing sales.', extra_tags="danger")
    except Exception as e:
        messages.error(request, f'Error deleting payment method: {e}', extra_tags="danger")
    return redirect('core:payment_method_list')

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
    today = date.today()
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