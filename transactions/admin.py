from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "ewaste_item",
        "status",
        "sale_price",
        "buyer_name",
        "date_sold",
        "created_at",
    )
    list_filter = ("status", "date_sold", "created_at")
    search_fields = ("ewaste_item__category__name", "buyer_name")
    autocomplete_fields = ("ewaste_item",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
