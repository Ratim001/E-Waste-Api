from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active", "date_joined")
    list_filter = (*BaseUserAdmin.list_filter, "role")
    search_fields = ("username", "email")
    ordering = ("username",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role information", {"fields": ("role",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"classes": ("wide",), "fields": ("role",)}),
    )
