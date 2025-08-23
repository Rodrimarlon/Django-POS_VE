from django.db import models
import django.utils.timezone
from customers.models import Customer
from products.models import Product
from core.models import PaymentMethod, ExchangeRate

class Sale(models.Model):
    date_added = models.DateTimeField(default=django.utils.timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, null=True)
    exchange_rate = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE, null=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_payed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ves = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igtf_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_credit = models.BooleanField(default=False)

    class Meta:
        db_table = 'Sales'

    def __str__(self) -> str:
        return f"Sale ID: {self.id} | Grand Total: {self.grand_total} | Datetime: {self.date_added}"

    def sum_items(self):
        details = SaleDetail.objects.filter(sale=self.id)
        return sum([d.quantity for d in details])


class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    total_detail = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'SaleDetails'

    def __str__(self) -> str:
        return f"Detail ID: {self.id} Sale ID: {self.sale.id} Quantity: {self.quantity}"


class CreditPayment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(default=django.utils.timezone.now)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    amount_ves = models.DecimalField(max_digits=10, decimal_places=2)
    exchange_rate = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Payment for sale {self.sale.id} of {self.amount_usd} USD'