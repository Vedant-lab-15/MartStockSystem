from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import F
from products.models import Product


class TransactionType(models.TextChoices):
    STOCK_IN = "IN", "Stock In (Restock)"
    STOCK_OUT = "OUT", "Stock Out (Sale)"
    ADJUSTMENT_INCREASE = "ADJ+", "Adjustment (Increase)"
    ADJUSTMENT_DECREASE = "ADJ-", "Adjustment (Decrease)"


class Transaction(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="transactions"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    transaction_type = models.CharField(
        max_length=4,
        choices=TransactionType.choices,
        default=TransactionType.STOCK_IN
    )
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transactions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        # Use select_for_update inside an atomic block to prevent race conditions
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=self.product_id)

            if self.transaction_type == TransactionType.STOCK_IN:
                Product.objects.filter(pk=product.pk).update(
                    stock_quantity=F('stock_quantity') + self.quantity
                )
            elif self.transaction_type == TransactionType.STOCK_OUT:
                Product.objects.filter(pk=product.pk).update(
                    stock_quantity=F('stock_quantity') - self.quantity
                )
            elif self.transaction_type == TransactionType.ADJUSTMENT_INCREASE:
                Product.objects.filter(pk=product.pk).update(
                    stock_quantity=F('stock_quantity') + self.quantity
                )
            elif self.transaction_type == TransactionType.ADJUSTMENT_DECREASE:
                Product.objects.filter(pk=product.pk).update(
                    stock_quantity=F('stock_quantity') - self.quantity
                )

            # Refresh to trigger post_save signal with updated value
            product.refresh_from_db()
            product.save()

            super().save(*args, **kwargs)


class StockAlert(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="alerts"
    )
    message = models.CharField(max_length=255)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alert for {self.product.name}: {self.message}"
