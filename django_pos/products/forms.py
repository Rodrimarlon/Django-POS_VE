from django import forms
from .models import Product, Category, Supplier

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'status', 'description', 'category', 'supplier', 'price_usd', 'stock', 'stock_min', 'photo', 'applies_iva']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'price_usd': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'applies_iva': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }