from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer
from products.models import Product

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name='details', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} for Order #{self.order.id}"