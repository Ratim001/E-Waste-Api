from django.db import models

from catalog.models import ItemCategory


class Transaction(models.Model):
    class StatusChoices(models.TextChoices):
        STOCKED = "stocked", "Stocked"
        SOLD = "sold", "Sold"

    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    weight_kg = models.DecimalField(max_digits=10, decimal_places=3)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    buyer_name = models.CharField(max_length=200)
    date_sold = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.STOCKED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["date_sold"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(sale_price__gte=0),
                name="transaction_sale_price_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(weight_kg__gt=0),
                name="transaction_weight_positive",
            ),
        ]

    def __str__(self):
        return f"Transaction for category {self.category_id} ({self.status})"
