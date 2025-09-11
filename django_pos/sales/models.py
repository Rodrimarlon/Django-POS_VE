from django.db import models
import django.utils.timezone
from customers.models import Customer
from products.models import Product
from core.models import PaymentMethod, ExchangeRate

from django.contrib.auth.models import User

class Sale(models.Model):
    """
    Represents a single sales transaction.
    """
    SALE_STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('pending_credit', 'Pending Credit'),
        ('partially_paid', 'Partially Paid'),
    )
    date_added = models.DateTimeField(default=django.utils.timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    exchange_rate = models.ForeignKey(ExchangeRate, on_delete=models.PROTECT, null=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ves = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igtf_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_credit = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=SALE_STATUS_CHOICES, default='completed')

    def __str__(self) -> str:
        return f"Sale ID: {self.id} | Grand Total: {self.grand_total} | Datetime: {self.date_added}"

    def get_balance(self):
        return (self.grand_total + self.igtf_amount) - self.amount_paid

    def sum_items(self):
        details = SaleDetail.objects.filter(sale=self.id)
        return sum([d.quantity for d in details])


class SaleDetail(models.Model):
    """
    Represents a single item within a sale.
    """
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    total_detail = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"Detail ID: {self.id} Sale ID: {self.sale.id} Quantity: {self.quantity}"


class Payment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Payment for sale {self.sale.id} of {self.amount} using {self.payment_method.name}'


class CreditPayment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(default=django.utils.timezone.now)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    amount_ves = models.DecimalField(max_digits=10, decimal_places=2)
    igtf_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exchange_rate = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Payment for sale {self.sale.id} of {self.amount_usd} USD'