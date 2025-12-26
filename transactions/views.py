from rest_framework import viewsets

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.select_related("ewaste_item", "ewaste_item__created_by")

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Transaction.objects.none()
        if user.is_staff or getattr(user, "role", "") == "admin":
            return self.queryset
        return self.queryset.filter(ewaste_item__created_by=user)
