from django.db import models
from datetime import datetime
from django.utils import timezone
import os, random
from django.utils.html import mark_safe


# -------------------------------
# Helper: Randomized image path
# -------------------------------
def image_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(10))
    return f'profile/{basefilename}_{randomstr}{file_extension}'


# -------------------------------
# User Account
# -------------------------------
class RegisAcc(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    position = models.CharField(max_length=50)
    user_image = models.ImageField(upload_to=image_path, default='profile/image.png')
    randomstrings = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})"

    def image_tag(self):
        return mark_safe(f'<img src="{self.user_image.url}" width="50" height="50" />')


# -------------------------------
# Products Table
# -------------------------------
class Products(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    product_condition = models.CharField(max_length=50, default='New')
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} - {self.model}"


# -------------------------------
# Sale (transaction record)
# -------------------------------
class Sale(models.Model):
    sale_date = models.DateTimeField(default=timezone.now)
    payment_mode = models.CharField(max_length=50, choices=[('Cash', 'Cash'), ('Card', 'Card')])
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Sale #{self.id} - {self.sale_date.strftime('%Y-%m-%d %H:%M')}"

    def update_totals(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.change = self.amount_received - total
        self.save()


# -------------------------------
# SaleItem (items per sale)
# -------------------------------
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        # When first saving → deduct stock
        if not self.pk:
            if self.product.quantity < self.quantity:
                raise ValueError("Not enough stock for this product.")
            self.product.quantity -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)
