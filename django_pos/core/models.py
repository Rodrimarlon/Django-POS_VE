from django.db import models
from django.contrib.auth.models import User

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    is_foreign_currency = models.BooleanField(default=False)
    requires_reference = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ExchangeRate(models.Model):
    date = models.DateField(unique=True)
    rate_usd_ves = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.date} - {self.rate_usd_ves}'

class Company(models.Model):
    name = models.CharField(max_length=256)
    tax_id = models.CharField(max_length=20)
    address = models.TextField()
    logo = models.ImageField(upload_to='company/', null=True, blank=True)

    def __str__(self):
        return self.name
