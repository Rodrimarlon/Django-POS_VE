from django.contrib import admin
from .models import Company, PaymentMethod, ExchangeRate

admin.site.register(Company)
admin.site.register(PaymentMethod)
admin.site.register(ExchangeRate)