from django import forms
from .models import PaymentMethod, Company

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['name', 'is_foreign_currency', 'requires_reference']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_foreign_currency': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_reference': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'tax_id', 'address', 'logo', 'igtf_percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'igtf_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }