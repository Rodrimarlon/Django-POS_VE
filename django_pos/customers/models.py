from django.db import models
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    """
    Represents a customer in the system, including details for credit management.
    """
    first_name = models.CharField(_("first name"), max_length=256)
    last_name = models.CharField(_("last name"), max_length=256, blank=True, default='')
    address = models.TextField(_("address"), max_length=256, blank=True, default='')
    email = models.EmailField(_("email"), max_length=256, blank=True, default='')
    phone = models.CharField(_("phone"), max_length=30, blank=True, default='')
    # tax_id must allow null values to enforce uniqueness on non-empty strings.
    tax_id = models.CharField(_("tax ID"), max_length=20, unique=True, null=True, blank=True)
    credit_limit = models.DecimalField(_("credit limit"), max_digits=10, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(_("outstanding balance"), max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self) -> str:
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def to_select2(self):
        return {
            'id': self.id,
            'text': self.get_full_name()
        }