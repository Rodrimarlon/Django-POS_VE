from django.db import models
import django.utils.timezone
from customers.models import Customer
from products.models import Product
from core.models import PaymentMethod, ExchangeRate
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User

class Sale(models.Model):
    """
    Represents a single sales transaction.
    """
    SALE_STATUS_CHOICES = (
        ('completed', _('Completed')),
        ('pending_credit', _('Pending Credit')),
        ('partially_paid', _('Partially Paid')),
    )
    date_added = models.DateTimeField(_("date added"), default=django.utils.timezone.now)
    customer = models.ForeignKey(Customer, verbose_name=_("customer"), on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.SET_NULL, null=True)
    exchange_rate = models.ForeignKey(ExchangeRate, verbose_name=_("exchange rate"), on_delete=models.PROTECT, null=True)
    sub_total = models.DecimalField(_("subtotal"), max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(_("grand total"), max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_("tax amount"), max_digits=10, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(_("tax percentage"), max_digits=10, decimal_places=2, default=0)
    amount_change = models.DecimalField(_("amount change"), max_digits=10, decimal_places=2, default=0)
    total_ves = models.DecimalField(_("total in VEF"), max_digits=10, decimal_places=2, default=0)
    igtf_amount = models.DecimalField(_("IGTF amount"), max_digits=10, decimal_places=2, default=0)
    is_credit = models.BooleanField(_("is credit"), default=False)
    amount_paid = models.DecimalField(_("amount paid"), max_digits=10, decimal_places=2, default=0)
    status = models.CharField(_("status"), max_length=20, choices=SALE_STATUS_CHOICES, default='completed')

    class Meta:
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")

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
    sale = models.ForeignKey(Sale, verbose_name=_("sale"), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.PROTECT)
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    quantity = models.IntegerField(_("quantity"))
    total_detail = models.DecimalField(_("total detail"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Sale Detail")
        verbose_name_plural = _("Sale Details")

    def __str__(self) -> str:
        return f"Detail ID: {self.id} Sale ID: {self.sale.id} Quantity: {self.quantity}"


class Payment(models.Model):
    sale = models.ForeignKey(Sale, verbose_name=_("sale"), on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_("payment method"), on_delete=models.PROTECT)
    amount = models.DecimalField(_("amount"), max_digits=10, decimal_places=2)
    reference = models.CharField(_("reference"), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    def __str__(self):
        return f'Payment for sale {self.sale.id} of {self.amount} using {self.payment_method.name}'


class CreditPayment(models.Model):
    sale = models.ForeignKey(Sale, verbose_name=_("sale"), on_delete=models.CASCADE)
    payment_date = models.DateTimeField(_("payment date"), default=django.utils.timezone.now)
    amount_usd = models.DecimalField(_("amount in USD"), max_digits=10, decimal_places=2)
    amount_ves = models.DecimalField(_("amount in VEF"), max_digits=10, decimal_places=2)
    igtf_amount = models.DecimalField(_("IGTF amount"), max_digits=10, decimal_places=2, default=0)
    exchange_rate = models.ForeignKey(ExchangeRate, verbose_name=_("exchange rate"), on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_("payment method"), on_delete=models.CASCADE)
    reference = models.CharField(_("reference"), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("Credit Payment")
        verbose_name_plural = _("Credit Payments")

    def __str__(self):
        return f'Payment for sale {self.sale.id} of {self.amount_usd} USD'