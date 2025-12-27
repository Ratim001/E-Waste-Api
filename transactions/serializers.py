from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    ewaste_item_detail = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_base_price_per_kg = serializers.DecimalField(
        source="category.base_price_per_kg",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Transaction
        fields = (
            "id",
            "category",
            "weight_kg",
            "ewaste_item_detail",
            "category_name",
            "category_base_price_per_kg",
            "sale_price",
            "buyer_name",
            "date_sold",
            "status",
            "created_at",
        )

    def get_ewaste_item_detail(self, obj):
        if not obj.category or not obj.weight_kg:
            return None
        return f"#{obj.category_id} | {obj.category.name} ({obj.weight_kg} kgs)"

    def validate(self, attrs):
        status_value = attrs.get("status") or getattr(self.instance, "status", None)
        date_sold = attrs.get("date_sold") or getattr(self.instance, "date_sold", None)
        if status_value == Transaction.StatusChoices.SOLD and not date_sold:
            raise serializers.ValidationError("date_sold is required when status is 'sold'.")
        if status_value == Transaction.StatusChoices.STOCKED and not attrs.get("date_sold"):
            attrs["date_sold"] = None
        return attrs
