from django.contrib import admin
from .models import DashboardPreference


@admin.register(DashboardPreference)
class DashboardPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'show_low_stock_first', 'items_per_page', 'preferred_view']
    list_filter = ['show_low_stock_first', 'preferred_view']
    search_fields = ['user__username']