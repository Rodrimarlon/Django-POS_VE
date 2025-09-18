from django.db import models
from django.forms import model_to_dict
from suppliers.models import Supplier
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """
    Represents a product category.
    """
    STATUS_CHOICES = (
        ("ACTIVE", _("Active")),
        ("INACTIVE", _("Inactive"))
    )

    name = models.CharField(_("name"), max_length=256)
    description = models.TextField(_("description"), max_length=256)
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=100,
        verbose_name=_("Status of the category"),
    )
    prefix = models.CharField(_("prefix"), max_length=3, unique=True, default='CAT')

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """
    Represents a product available for sale, including stock details.
    """
    STATUS_CHOICES = (
        ("ACTIVE", _("Active")),
        ("INACTIVE", _("Inactive"))
    )

    sku = models.CharField(_("SKU"), max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(_("name"), max_length=256)
    description = models.TextField(_("description"), max_length=256)
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=100,
        verbose_name=_("Status of the product"),
    )
    category = models.ForeignKey(
        Category, verbose_name=_("category"), related_name="products", on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, verbose_name=_("supplier"), on_delete=models.PROTECT, null=True)
    price_usd = models.DecimalField(_("price in USD"), max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(_("stock"), default=0)
    stock_min = models.IntegerField(_("minimum stock"), default=0)
    photo = models.ImageField(_("photo"), upload_to='products/', null=True, blank=True)
    applies_iva = models.BooleanField(_("applies VAT"), default=False)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.sku:
            last_product = Product.objects.filter(category=self.category).order_by('-sku').first()
            if last_product and last_product.sku:
                # Extract the numeric part of the SKU
                last_sku_num = int(last_product.sku[len(self.category.prefix):])
                new_sku_num = last_sku_num + 1
            else:
                new_sku_num = 1
            
            # Format the new SKU with leading zeros
            self.sku = f"{self.category.prefix}{new_sku_num:04d}"
        super().save(*args, **kwargs)

    def to_json(self):
        item = model_to_dict(self)
        item['id'] = self.id
        item['text'] = self.name
        item['category'] = self.category.name
        item['quantity'] = 1
        item['total_product'] = 0
        item['price'] = str(self.price_usd)
        return item


class InventoryMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = (
        ('in', _('In')),
        ('out', _('Out')),
        ('adjustment', _('Adjustment')),
    )

    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.CASCADE)
    movement_type = models.CharField(_("movement type"), max_length=10, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField(_("quantity"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.SET_NULL, null=True)
    reason = models.CharField(_("reason"), max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.get_movement_type_display()} of {self.quantity} for {self.product.name} on {self.created_at}'

    class Meta:
        verbose_name = _('Inventory Movement')
        verbose_name_plural = _('Inventory Movements')
        ordering = ['-created_at']