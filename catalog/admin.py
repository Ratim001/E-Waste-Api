from django.contrib import admin

from .models import ItemCategory


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price_per_kg")
    search_fields = ("name",)
    ordering = ("name",)
