from django.db import models


class Supplier(models.Model):
    supplier_name = models.CharField(max_length=200)
    contact = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["supplier_name"]

    def __str__(self):
        return self.supplier_name
