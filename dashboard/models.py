from django.db import models
from django.conf import settings


class DashboardPreference(models.Model):
    """Store user preferences for dashboard views"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_preference"
    )
    show_low_stock_first = models.BooleanField(default=True)
    items_per_page = models.PositiveIntegerField(default=20)
    preferred_view = models.CharField(
        max_length=10,
        choices=[
            ('list', 'List View'),
            ('grid', 'Grid View'),
        ],
        default='list'
    )
    
    def __str__(self):
        return f"Dashboard preferences for {self.user.username}"