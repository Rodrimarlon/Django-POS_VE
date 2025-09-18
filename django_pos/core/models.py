from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class PaymentMethod(models.Model):
    name = models.CharField(_("name"), max_length=100)
    is_foreign_currency = models.BooleanField(_("is foreign currency"), default=False)
    requires_reference = models.BooleanField(_("requires reference"), default=False)

    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")

    def __str__(self):
        return self.name

class ExchangeRate(models.Model):
    date = models.DateField(_("date"), unique=True)
    rate_usd_ves = models.DecimalField(_("rate USD to VEF"), max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("Exchange Rate")
        verbose_name_plural = _("Exchange Rates")

    def __str__(self):
        return f'{self.date} - {self.rate_usd_ves}'

class Company(models.Model):
    name = models.CharField(_("name"), max_length=256)
    tax_id = models.CharField(_("tax ID"), max_length=20)
    address = models.TextField(_("address"))
    logo = models.ImageField(_("logo"), upload_to='company/', null=True, blank=True)
    igtf_percentage = models.DecimalField(_("IGTF percentage"), max_digits=5, decimal_places=2, default=3.00)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.name
