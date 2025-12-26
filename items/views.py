from rest_framework import decorators, permissions, response, status, viewsets

from .models import EWasteItem
from .serializers import EWasteItemSerializer


class EWasteItemViewSet(viewsets.ModelViewSet):
    serializer_class = EWasteItemSerializer
    queryset = EWasteItem.objects.select_related("category", "source_supplier", "created_by")

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return EWasteItem.objects.none()
        if user.is_staff or getattr(user, "role", "") == "admin":
            return self.queryset
        return self.queryset.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @decorators.action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def estimate_price(self, request, pk=None):
        item = self.get_object()
        estimate = item.compute_estimated_value()
        return response.Response({"estimated_value": estimate}, status=status.HTTP_200_OK)
