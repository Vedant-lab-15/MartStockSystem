from django.contrib import admin
from .models import Transaction, StockAlert


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'transaction_type', 'unit_price', 'created_by', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['product__name', 'notes']
    date_hierarchy = 'created_at'
    raw_id_fields = ['product', 'created_by']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ['product', 'quantity', 'transaction_type', 'unit_price', 'created_by', 'created_at']
        return []


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'message', 'is_resolved', 'created_at', 'resolved_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['product__name', 'message']
    date_hierarchy = 'created_at'
    list_editable = ['is_resolved']