from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Transaction, StockAlert
from .serializers import TransactionSerializer, StockAlertSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('product', 'created_by')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    http_method_names = ['get', 'post', 'head', 'options']  # transactions are immutable

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('product'):
            qs = qs.filter(product_id=self.request.query_params['product'])
        if self.request.query_params.get('type'):
            qs = qs.filter(transaction_type=self.request.query_params['type'])
        return qs


class StockAlertViewSet(viewsets.ModelViewSet):
    queryset = StockAlert.objects.select_related('product')
    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        return Response({'status': 'resolved'})
