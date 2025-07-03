from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from products.models import Product


class TransactionType(models.TextChoices):
    STOCK_IN = "IN", "Stock In (Restock)"
    STOCK_OUT = "OUT", "Stock Out (Sale)"
    ADJUSTMENT = "ADJ", "Adjustment"


class Transaction(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="transactions"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    transaction_type = models.CharField(
        max_length=3, 
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
        # Update product stock quantity
        product = self.product
        
        if self.transaction_type == TransactionType.STOCK_IN:
            product.stock_quantity += self.quantity
        elif self.transaction_type == TransactionType.STOCK_OUT:
            # Ensure we don't go below 0
            product.stock_quantity = max(0, product.stock_quantity - self.quantity)
        elif self.transaction_type == TransactionType.ADJUSTMENT:
            # For adjustments, quantity can be positive or negative
            # We're using the absolute value of quantity in the model,
            # so we determine if it's an increase or decrease from the notes
            if "decrease" in self.notes.lower():
                product.stock_quantity = max(0, product.stock_quantity - self.quantity)
            else:
                product.stock_quantity += self.quantity
        
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