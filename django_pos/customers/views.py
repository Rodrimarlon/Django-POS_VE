from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import Customer
from .forms import CustomerForm
from authentication.decorators import admin_required, role_required
from django.db import IntegrityError

@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def customers_list_view(request):
    context = {
        "active_icon": "customers",
        "customers": Customer.objects.all()
    }
    return render(request, "customers/customers.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def customers_add_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Customer created successfully!', extra_tags="success")
                return redirect('customers:customers_list')
            except IntegrityError:
                messages.error(request, 'Customer with this Tax ID already exists.', extra_tags="danger")
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = CustomerForm()

    context = {
        "active_icon": "customers",
        "form": form,
    }
    return render(request, "customers/customers_add.html", context=context)

@role_required(allowed_roles=['admin', 'cashier'])
@login_required(login_url="/accounts/login/")
def customers_update_view(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer not found!', extra_tags="danger")
        return redirect('customers:customers_list')

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Customer updated successfully!', extra_tags="success")
                return redirect('customers:customers_list')
            except IntegrityError:
                messages.error(request, 'Customer with this Tax ID already exists.', extra_tags="danger")
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = CustomerForm(instance=customer)

    context = {
        "active_icon": "customers",
        "form": form,
        "customer": customer,
    }
    return render(request, "customers/customers_update.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def customers_delete_view(request, customer_id):
    """
    Args:
        request:
        customer_id : The customer's ID that will be deleted
    """
    try:
        customer = Customer.objects.get(id=customer_id)
        customer.delete()
        messages.success(request, 'Customer: ' + customer.get_full_name() +
                         ' deleted!', extra_tags="success")
        return redirect('customers:customers_list')
    except Exception as e:
        messages.success(
            request, 'There was an error during the elimination!', extra_tags="danger")
        print(e)
        return redirect('customers:customers_list')

@login_required(login_url="/accounts/login/")
def get_customers_ajax_view(request):
    if request.method == 'POST':
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            data = []
            term = request.POST.get('term', '')
            print(f"Customer search term: {term}")
            
            customers = Customer.objects.filter(
                Q(first_name__icontains=term) | 
                Q(last_name__icontains=term) | 
                Q(tax_id__icontains=term)
            )[:10] # Limit to 10 results
            print(f"Found customers: {customers.count()}")

            for customer in customers:
                data.append({
                    'id': customer.id,
                    'text': customer.get_full_name() + (f' ({customer.tax_id})' if customer.tax_id else '')
                })
            print(f"Returning data: {data}")
            return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False) # Return empty list for non-POST/AJAX requests

@admin_required
@login_required(login_url="/accounts/login/")
def customer_purchase_history_view(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        sales = Sale.objects.filter(customer=customer).order_by('-date_added') # Order by date descending

        context = {
            "active_icon": "customers", # Or "reports" if a separate reports section is desired
            "customer": customer,
            "sales": sales,
        }
        return render(request, "customers/customer_purchase_history.html", context)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer not found!', extra_tags="danger")
        return redirect('customers:customers_list')
    except Exception as e:
        messages.error(request, f'An error occurred: {e}', extra_tags="danger")
        return redirect('customers:customers_list')
