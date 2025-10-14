from django.db import models
from django.utils import timezone

class Products(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    product_condition = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="Available")

    def __str__(self):
        return f"{self.brand} {self.model}"

    @property
    def total_value(self):
        return self.quantity * self.price


class Sale(models.Model):
    sale_date = models.DateTimeField(default=timezone.now)
    payment_mode = models.CharField(max_length=50, choices=[("Cash", "Cash"), ("Card", "Card")])
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Sale #{self.id} - {self.sale_date.strftime('%Y-%m-%d %H:%M')}"

    def update_totals(self):
        self.total_price = sum(item.subtotal for item in self.items.all())
        self.change = self.amount_received - self.total_price
        self.save()


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        # Deduct stock when item is saved
        if not self.pk:
            if self.product.quantity < self.quantity:
                raise ValueError("Not enough stock for this product.")
            self.product.quantity -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)
