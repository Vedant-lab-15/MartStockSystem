from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    date_hierarchy = 'created_at'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'sku', 'price', 'stock_quantity', 'is_low_stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'is_active']
    date_hierarchy = 'created_at'
    readonly_fields = ['is_low_stock']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'sku', 'description', 'image')
        }),
        ('Pricing Information', {
            'fields': ('price', 'cost_price')
        }),
        ('Stock Information', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'is_low_stock')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'