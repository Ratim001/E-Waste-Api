from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "weight_kg",
        "status",
        "sale_price",
        "buyer_name",
        "date_sold",
        "created_at",
    )
    list_filter = ("status", "category", "date_sold", "created_at")
    search_fields = ("category__name", "buyer_name")
    autocomplete_fields = ("category",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
