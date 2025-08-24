from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Supplier
from .forms import SupplierForm  # Import the new form
from authentication.decorators import admin_required
from django.db import IntegrityError

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
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Supplier created successfully!', extra_tags="success")
                return redirect('suppliers:supplier_list')
            except IntegrityError:
                messages.error(request, 'A supplier with that Tax ID already exists.', extra_tags="danger")
        else:
            # Pass the form with errors back to the template
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = SupplierForm()

    context = {
        "active_icon": "suppliers",
        "form": form,
    }
    return render(request, "suppliers/suppliers_add.html", context=context)

@admin_required
@login_required(login_url="/accounts/login/")
def supplier_update_view(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        messages.error(request, 'Supplier not found!', extra_tags="danger")
        return redirect('suppliers:supplier_list')

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Supplier updated successfully!', extra_tags="success")
                return redirect('suppliers:supplier_list')
            except IntegrityError:
                messages.error(request, 'A supplier with that Tax ID already exists.', extra_tags="danger")
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = SupplierForm(instance=supplier)

    context = {
        "active_icon": "suppliers",
        "form": form,
    }
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
    except IntegrityError:
        # This will be triggered if a product is linked to this supplier due to on_delete=PROTECT
        messages.error(request, 'Cannot delete this supplier because they are linked to existing products.', extra_tags="danger")
    except Exception as e:
        messages.error(request, f'Error deleting supplier: {e}', extra_tags="danger")
    return redirect('suppliers:supplier_list')