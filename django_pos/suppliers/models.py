from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=256)
    tax_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name
