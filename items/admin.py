from django.contrib import admin

from .models import EWasteItem


@admin.register(EWasteItem)
class EWasteItemAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "weight_kg",
        "condition",
        "source_supplier",
        "date_collected",
        "estimated_value",
        "created_by",
    )
    list_filter = ("condition", "category", "source_supplier", "date_collected")
    search_fields = ("category__name", "source_supplier__supplier_name", "created_by__username")
    autocomplete_fields = ("category", "source_supplier", "created_by")
    date_hierarchy = "date_collected"
    ordering = ("-date_collected", "-created_at")
