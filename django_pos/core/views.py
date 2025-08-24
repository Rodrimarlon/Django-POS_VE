from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PaymentMethod, Company, ExchangeRate
from datetime import date

@login_required(login_url="/accounts/login/")
def payment_method_list_view(request):
    context = {
        "active_icon": "payment_methods",
        "payment_methods": PaymentMethod.objects.all()
    }
    return render(request, "core/payment_methods.html", context=context)

@login_required(login_url="/accounts/login/")
def payment_method_add_view(request):
    context = {
        "active_icon": "payment_methods",
    }
    if request.method == 'POST':
        data = request.POST
        attributes = {
            "name": data['name'],
            "is_foreign_currency": 'is_foreign_currency' in data,
            "requires_reference": 'requires_reference' in data,
        }
        try:
            PaymentMethod.objects.create(**attributes)
            messages.success(request, 'Payment method created successfully!', extra_tags="success")
            return redirect('core:payment_method_list')
        except Exception as e:
            messages.error(request, f'Error creating payment method: {e}', extra_tags="danger")
            return redirect('core:payment_method_add')
    return render(request, "core/payment_methods_add.html", context=context)

@login_required(login_url="/accounts/login/")
def payment_method_update_view(request, payment_method_id):
    try:
        payment_method = PaymentMethod.objects.get(id=payment_method_id)
    except PaymentMethod.DoesNotExist:
        messages.error(request, 'Payment method not found!', extra_tags="danger")
        return redirect('core:payment_method_list')

    context = {
        "active_icon": "payment_methods",
        "payment_method": payment_method,
    }
    if request.method == 'POST':
        data = request.POST
        attributes = {
            "name": data['name'],
            "is_foreign_currency": 'is_foreign_currency' in data,
            "requires_reference": 'requires_reference' in data,
        }
        try:
            PaymentMethod.objects.filter(id=payment_method_id).update(**attributes)
            messages.success(request, 'Payment method updated successfully!', extra_tags="success")
            return redirect('core:payment_method_list')
        except Exception as e:
            messages.error(request, f'Error updating payment method: {e}', extra_tags="danger")
            return redirect('core:payment_method_update', payment_method_id=payment_method_id)
    return render(request, "core/payment_methods_update.html", context=context)

@login_required(login_url="/accounts/login/")
def payment_method_delete_view(request, payment_method_id):
    try:
        payment_method = PaymentMethod.objects.get(id=payment_method_id)
        payment_method.delete()
        messages.success(request, 'Payment method deleted successfully!', extra_tags="success")
    except PaymentMethod.DoesNotExist:
        messages.error(request, 'Payment method not found!', extra_tags="danger")
    except Exception as e:
        messages.error(request, f'Error deleting payment method: {e}', extra_tags="danger")
    return redirect('core:payment_method_list')

@login_required(login_url="/accounts/login/")
def company_view(request):
    company = Company.objects.first()
    context = {
        "active_icon": "company",
        "company": company,
    }
    return render(request, "core/company.html", context=context)

@login_required(login_url="/accounts/login/")
def company_update_view(request):
    company = Company.objects.first()
    if request.method == 'POST':
        data = request.POST
        attributes = {
            "name": data['name'],
            "tax_id": data['tax_id'],
            "address": data['address'],
        }
        # Handle logo upload
        if 'logo' in request.FILES:
            attributes['logo'] = request.FILES['logo']

        if company:
            # Update existing company
            Company.objects.filter(id=company.id).update(**attributes)
            messages.success(request, 'Company updated successfully!', extra_tags="success")
        else:
            # Create new company
            Company.objects.create(**attributes)
            messages.success(request, 'Company created successfully!', extra_tags="success")
        return redirect('core:company_view')
    
    context = {
        "active_icon": "company",
        "company": company,
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

@login_required(login_url="/accounts/login/")
def exchange_rate_list_view(request):
    context = {
        "active_icon": "exchange_rates",
        "exchange_rates": ExchangeRate.objects.all().order_by('-date')
    }
    return render(request, "core/exchange_rates.html", context=context)
