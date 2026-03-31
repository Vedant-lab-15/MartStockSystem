from rest_framework import serializers
from .models import Transaction, StockAlert


class TransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'product', 'product_name', 'quantity', 'transaction_type',
            'unit_price', 'notes', 'created_by', 'created_by_username', 'created_at',
        ]
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class StockAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StockAlert
        fields = ['id', 'product', 'product_name', 'message', 'is_resolved', 'created_at', 'resolved_at']
        read_only_fields = ['created_at']
