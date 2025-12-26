from datetime import date

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from rest_framework import permissions, response, views

from items.models import EWasteItem
from suppliers.models import Supplier


class TodayAnalyticsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = date.today()
        qs = EWasteItem.objects.filter(date_collected=today)
        aggregates = qs.aggregate(
            total_weight=Sum("weight_kg"),
            total_estimated_value=Sum("estimated_value"),
        )
        data = {
            "date": today.isoformat(),
            "total_weight_kg": float(aggregates["total_weight"] or 0),
            "total_estimated_value": float(aggregates["total_estimated_value"] or 0),
            "items_collected": qs.count(),
        }
        return response.Response(data)


class MonthlyAnalyticsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = (
            EWasteItem.objects.annotate(month=TruncMonth("date_collected"))
            .values("month")
            .annotate(
                total_weight=Sum("weight_kg"),
                total_estimated_value=Sum("estimated_value"),
                items_collected=Count("id"),
            )
            .order_by("month")
        )
        results = [
            {
                "month": entry["month"].strftime("%Y-%m") if entry["month"] else None,
                "total_weight_kg": float(entry["total_weight"] or 0),
                "total_estimated_value": float(entry["total_estimated_value"] or 0),
                "items_collected": entry["items_collected"],
            }
            for entry in qs
        ]
        return response.Response({"monthly": results})


class SupplierRankingView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = (
            Supplier.objects.annotate(
                total_estimated_value=Sum("items__estimated_value"),
                item_count=Count("items"),
            )
            .order_by("-total_estimated_value")
        )
        ranking = [
            {
                "supplier_id": supplier.id,
                "supplier_name": supplier.supplier_name,
                "total_estimated_value": float(supplier.total_estimated_value or 0),
                "item_count": supplier.item_count,
            }
            for supplier in qs
        ]
        return response.Response({"ranking": ranking})
