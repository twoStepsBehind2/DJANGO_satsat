from django.db import models

class RegisAcc(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)  # Better to hash passwords, not store plain text
    position = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.position})"
