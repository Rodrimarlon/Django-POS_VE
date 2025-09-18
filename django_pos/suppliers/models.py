from django.db import models
from django.utils.translation import gettext_lazy as _

class Supplier(models.Model):
    name = models.CharField(_("name"), max_length=256)
    tax_id = models.CharField(_("tax ID"), max_length=20, unique=True)
    phone = models.CharField(_("phone"), max_length=20)
    email = models.EmailField(_("email"))
    address = models.TextField(_("address"))

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")

    def __str__(self):
        return self.name
