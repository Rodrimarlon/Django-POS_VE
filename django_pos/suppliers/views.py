from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Supplier
from authentication.decorators import admin_required

@admin_required
@login_required(login_url="/accounts/login/")
def supplier_list_view(request):
    context = {
        "active_icon": "suppliers",
        "suppliers": Supplier.objects.all()
    }
    return render(request, "suppliers/suppliers.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def supplier_add_view(request):
    context = {
        "active_icon": "suppliers",
    }
    if request.method == 'POST':
        data = request.POST
        attributes = {
            "name": data['name'],
            "tax_id": data['tax_id'],
            "phone": data['phone'],
            "email": data['email'],
            "address": data['address'],
        }
        try:
            Supplier.objects.create(**attributes)
            messages.success(request, 'Supplier created successfully!', extra_tags="success")
            return redirect('suppliers:supplier_list')
        except Exception as e:
            messages.error(request, f'Error creating supplier: {e}', extra_tags="danger")
            return redirect('suppliers:supplier_add')
    return render(request, "suppliers/suppliers_add.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def supplier_update_view(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        messages.error(request, 'Supplier not found!', extra_tags="danger")
        return redirect('suppliers:supplier_list')

    context = {
        "active_icon": "suppliers",
        "supplier": supplier,
    }
    if request.method == 'POST':
        data = request.POST
        attributes = {
            "name": data['name'],
            "tax_id": data['tax_id'],
            "phone": data['phone'],
            "email": data['email'],
            "address": data['address'],
        }
        try:
            Supplier.objects.filter(id=supplier_id).update(**attributes)
            messages.success(request, 'Supplier updated successfully!', extra_tags="success")
            return redirect('suppliers:supplier_list')
        except Exception as e:
            messages.error(request, f'Error updating supplier: {e}', extra_tags="danger")
            return redirect('suppliers:supplier_update', supplier_id=supplier_id)
    return render(request, "suppliers/suppliers_update.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def supplier_delete_view(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully!', extra_tags="success")
    except Supplier.DoesNotExist:
        messages.error(request, 'Supplier not found!', extra_tags="danger")
    except Exception as e:
        messages.error(request, f'Error deleting supplier: {e}', extra_tags="danger")
    return redirect('suppliers:supplier_list')