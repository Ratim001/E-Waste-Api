from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("supplier_name", "contact", "location")
    search_fields = ("supplier_name", "contact", "location")
    ordering = ("supplier_name",)
