from django.contrib.auth import get_user_model
from rest_framework import serializers

from catalog.models import ItemCategory
from suppliers.models import Supplier

from .models import EWasteItem


class EWasteItemSerializer(serializers.ModelSerializer):
    estimated_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    category_detail = serializers.CharField(source="category.name", read_only=True)
    supplier_detail = serializers.CharField(source="source_supplier.supplier_name", read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = EWasteItem
        fields = (
            "id",
            "category",
            "category_detail",
            "weight_kg",
            "condition",
            "source_supplier",
            "supplier_detail",
            "date_collected",
            "estimated_value",
            "created_by",
            "created_at",
        )

    def validate_condition(self, value):
        valid_values = {choice[0] for choice in EWasteItem.ConditionChoices.choices}
        if value not in valid_values:
            raise serializers.ValidationError("Invalid condition value.")
        return value

    def validate_category(self, value):
        if not isinstance(value, ItemCategory):
            raise serializers.ValidationError("Invalid category.")
        return value

    def validate_source_supplier(self, value):
        if value is not None and not isinstance(value, Supplier):
            raise serializers.ValidationError("Invalid supplier.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
