from decimal import Decimal

from django.conf import settings
from django.db import models

from catalog.models import ItemCategory
from suppliers.models import Supplier


class EWasteItem(models.Model):
    class ConditionChoices(models.TextChoices):
        POOR = "poor", "Poor"
        FAIR = "fair", "Fair"
        GOOD = "good", "Good"

    CONDITION_MULTIPLIERS = {
        ConditionChoices.POOR: Decimal("0.8"),
        ConditionChoices.FAIR: Decimal("0.9"),
        ConditionChoices.GOOD: Decimal("1.0"),
    }

    category = models.ForeignKey(
        ItemCategory, on_delete=models.PROTECT, related_name="items"
    )
    weight_kg = models.DecimalField(max_digits=10, decimal_places=3)
    condition = models.CharField(max_length=20, choices=ConditionChoices.choices)
    source_supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    date_collected = models.DateField()
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ewaste_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_collected", "-created_at"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["date_collected"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["source_supplier"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(weight_kg__gt=0),
                name="item_weight_positive",
            )
        ]

    def compute_estimated_value(self):
        multiplier = self.CONDITION_MULTIPLIERS.get(self.condition, Decimal("1"))
        base_price = self.category.base_price_per_kg
        estimated = Decimal(base_price) * Decimal(self.weight_kg) * multiplier
        return estimated.quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        if self.category_id and self.weight_kg and self.condition:
            self.estimated_value = self.compute_estimated_value()
        super().save(*args, **kwargs)

    def __str__(self):
        item_id = self.id or "unsaved"
        return f"#{item_id} | {self.category.name} ({self.weight_kg} kg)"
