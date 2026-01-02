from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import RegisterView
from analytics.views import (
    MonthlyAnalyticsView,
    SupplierRankingView,
    TodayAnalyticsView,
)
from catalog.views import ItemCategoryViewSet
from items.views import EWasteItemViewSet
from suppliers.views import SupplierViewSet
from transactions.views import TransactionViewSet

router = DefaultRouter()
router.register("categories", ItemCategoryViewSet, basename="category")
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("items", EWasteItemViewSet, basename="item")
router.register("transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("analytics/today/", TodayAnalyticsView.as_view(), name="analytics-today"),
    path("analytics/monthly/", MonthlyAnalyticsView.as_view(), name="analytics-monthly"),
    path("analytics/supplier-ranking/", SupplierRankingView.as_view(), name="analytics-suppliers"),
    path("", include(router.urls)),
]
