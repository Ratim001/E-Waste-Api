from django.db import models


class ItemCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(base_price_per_kg__gte=0),
                name="category_base_price_non_negative",
            )
        ]

    def __str__(self):
        return self.name
