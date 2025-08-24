from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Customer


@login_required(login_url="/accounts/login/")
def customers_list_view(request):
    context = {
        "active_icon": "customers",
        "customers": Customer.objects.all()
    }
    return render(request, "customers/customers.html", context=context)


@login_required(login_url="/accounts/login/")
def customers_add_view(request):
    context = {
        "active_icon": "customers",
    }

    if request.method == 'POST':
        # Save the POST arguments
        data = request.POST

        attributes = {
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "address": data['address'],
            "email": data['email'],
            "phone": data['phone'],
            "tax_id": data.get('tax_id'),  # Use .get for optional fields
            "credit_limit": data.get('credit_limit', 0),  # Provide default value
            "outstanding_balance": 0,  # Default to 0 for new customers
        }

        # Check if a customer with the same attributes exists
        if Customer.objects.filter(tax_id=attributes['tax_id']).exists():
            messages.error(request, 'Customer with this Tax ID already exists!',
                           extra_tags="warning")
            return redirect('customers:customers_add')

        try:
            # Create the customer
            new_customer = Customer.objects.create(**attributes)

            # If it doesn't exist save it
            new_customer.save()

            messages.success(request, 'Customer: ' + attributes["first_name"] + " " +
                             attributes["last_name"] + ' created successfully!', extra_tags="success")
            return redirect('customers:customers_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the creation!', extra_tags="danger")
            print(e)
            return redirect('customers:customers_add')

    return render(request, "customers/customers_add.html", context=context)


@login_required(login_url="/accounts/login/")
def customers_update_view(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer not found!', extra_tags="danger")
        return redirect('customers:customers_list')

    context = {
        "active_icon": "customers",
        "customer": customer,
    }

    if request.method == 'POST':
        data = request.POST
        attributes = {
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "address": data['address'],
            "email": data['email'],
            "phone": data['phone'],
            "tax_id": data.get('tax_id'),
            "credit_limit": data.get('credit_limit', 0),
        }

        # Check if a customer with the same tax_id already exists (excluding the current customer)
        if Customer.objects.filter(tax_id=attributes['tax_id']).exclude(id=customer_id).exists():
            messages.error(request, 'Customer with this Tax ID already exists!', extra_tags="danger")
            return redirect('customers:customers_update', customer_id=customer_id)

        try:
            Customer.objects.filter(id=customer_id).update(**attributes)
            messages.success(request, 'Customer updated successfully!', extra_tags="success")
            return redirect('customers:customers_list')
        except Exception as e:
            messages.error(request, f'Error updating customer: {e}', extra_tags="danger")
            print(e)
            return redirect('customers:customers_update', customer_id=customer_id)

    return render(request, "customers/customers_update.html", context=context)


@login_required(login_url="/accounts/login/")
def customers_delete_view(request, customer_id):
    """
    Args:
        request:
        customer_id : The customer's ID that will be deleted
    """
    try:
        # Get the customer to delete
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