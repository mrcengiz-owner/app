from django.db import models
from django.utils import timezone

class Company(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    product_code = models.CharField(max_length=100, unique=False)
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Yeni eklenecek alan
    size = models.CharField(max_length=50)  # Size alanı eklendi
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
