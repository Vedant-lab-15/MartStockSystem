from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Product
from transactions.models import StockAlert


@receiver(post_save, sender=Product)
def check_stock_level(sender, instance, **kwargs):
    """Create stock alerts when product stock falls below threshold"""
    if instance.is_low_stock:
        # Check if there's an unresolved alert already
        existing_unresolved = StockAlert.objects.filter(
            product=instance, is_resolved=False
        ).exists()
        
        if not existing_unresolved:
            StockAlert.objects.create(
                product=instance,
                message=f"Low stock alert: {instance.name} has only {instance.stock_quantity} units left (threshold: {instance.low_stock_threshold}).",
            )