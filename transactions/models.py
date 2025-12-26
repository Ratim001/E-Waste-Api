from django.db import models

from items.models import EWasteItem


class Transaction(models.Model):
    class StatusChoices(models.TextChoices):
        STOCKED = "stocked", "Stocked"
        SOLD = "sold", "Sold"

    ewaste_item = models.ForeignKey(
        EWasteItem, on_delete=models.CASCADE, related_name="transactions"
    )
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
            models.Index(fields=["ewaste_item"]),
            models.Index(fields=["date_sold"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(sale_price__gte=0),
                name="transaction_sale_price_non_negative",
            )
        ]

    def __str__(self):
        return f"Transaction for {self.ewaste_item_id} ({self.status})"
