from django.db import models
from datetime import datetime
from django.utils import timezone
import os, random
from django.utils.html import mark_safe
from django.db import models

now = timezone.now()

def image_path(instance, filename):
    basefilename, file_extention= os.path.splitext(filename)
    chars ='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr =''.join((random.choice(chars)) for x in range(10))
    _now = datetime.now()

    return 'profile/{basename}_{randomstring}{ext}'.format(basename=basefilename, randomstring=randomstr, ext=file_extention)

class RegisAcc(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)  # Better to hash passwords, not store plain text
    position = models.CharField(max_length=50)
    user_image = models.ImageField(upload_to=image_path, default='profile/image.png')
    randomstrings = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})"
    
    def image_tag(self):
        return mark_safe(f'<img src="{self.user_image.url}" width="50" height="50" />')
    
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