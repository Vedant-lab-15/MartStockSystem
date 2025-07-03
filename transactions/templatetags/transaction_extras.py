from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the arg by the value."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return None

@register.filter
def filter_low_stock(products, threshold=10):
    """
    Filter products with stock less than or equal to the threshold.
    Usage: {% for product in products|filter_low_stock:5 %}
    """
    return [product for product in products if product.stock <= threshold]
