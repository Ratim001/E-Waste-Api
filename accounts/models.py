from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = "admin", "Admin"
        COLLECTOR = "collector", "Collector"

    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.COLLECTOR)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.role == self.RoleChoices.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)
