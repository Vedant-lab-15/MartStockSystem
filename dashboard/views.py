from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, IntegerField
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta

from products.models import Product, Category
from transactions.models import Transaction, StockAlert, TransactionType
from .models import DashboardPreference


@login_required
def dashboard_home(request):
    """Main dashboard view showing summary statistics and low stock items."""
    
    # Get user's dashboard preferences or use defaults
    try:
        pref = request.user.dashboard_preference
    except:
        pref = DashboardPreference(
            user=request.user,
            show_low_stock_first=True,
            items_per_page=20,
            preferred_view='list'
        )
        pref.save()
    
    # Get low stock products
    low_stock_products = [p for p in Product.objects.all() if p.is_low_stock]
    
    # Get overall stock statistics
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_stock_value = sum(p.price * p.stock_quantity for p in Product.objects.all())
    
    # Get today's transactions
    today = timezone.now().date()
    today_transactions = Transaction.objects.filter(created_at__date=today)
    today_stock_in = today_transactions.filter(transaction_type=TransactionType.STOCK_IN)
    today_stock_out = today_transactions.filter(transaction_type=TransactionType.STOCK_OUT)
    today_stock_in_value = sum(t.unit_price * t.quantity for t in today_stock_in)
    today_stock_out_value = sum(t.unit_price * t.quantity for t in today_stock_out)
    
    # Get recent transactions
    recent_transactions = Transaction.objects.all().order_by('-created_at')[:10]
    
    # Get unresolved alerts
    unresolved_alerts = StockAlert.objects.filter(is_resolved=False)
    
    context = {
        'low_stock_products': low_stock_products,
        'total_products': total_products,
        'active_products': active_products,
        'total_stock_value': total_stock_value,
        'today_stock_in_count': today_stock_in.count(),
        'today_stock_out_count': today_stock_out.count(),
        'today_stock_in_value': today_stock_in_value,
        'today_stock_out_value': today_stock_out_value,
        'recent_transactions': recent_transactions,
        'unresolved_alerts': unresolved_alerts,
        'preferences': pref,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard_reports(request):
    """Generate various reports for management review."""
    report_type = request.GET.get('type', 'stock')
    time_period = request.GET.get('period', '30')  # Default to 30 days
    
    # Calculate date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=int(time_period))
    
    context = {
        'report_type': report_type,
        'time_period': time_period,
        'start_date': start_date.date(),
        'end_date': end_date.date(),
    }
    
    if report_type == 'stock':
        # Stock level report
        context['categories'] = Category.objects.all()
        context['products'] = Product.objects.all().order_by('category__name', 'name')
        context['low_stock_count'] = len([p for p in Product.objects.all() if p.is_low_stock])
        
    elif report_type == 'sales':
        # Sales report
        sales = Transaction.objects.filter(
            transaction_type=TransactionType.STOCK_OUT,
            created_at__range=[start_date, end_date]
        )
        
        # Group by day
        daily_sales = sales.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            total_amount=Sum(F('quantity') * F('unit_price')),
            count=Count('id')
        ).order_by('day')
        
        # Group by product
        product_sales = sales.values(
            'product__name'
        ).annotate(
            total_amount=Sum(F('quantity') * F('unit_price')),
            count=Sum('quantity')
        ).order_by('-total_amount')
        
        # Group by category
        category_sales = sales.values(
            'product__category__name'
        ).annotate(
            total_amount=Sum(F('quantity') * F('unit_price')),
            count=Sum('quantity')
        ).order_by('-total_amount')
        
        context.update({
            'daily_sales': daily_sales,
            'product_sales': product_sales,
            'category_sales': category_sales,
            'total_sales': sales.aggregate(
                total=Sum(F('quantity') * F('unit_price'))
            )['total'] or 0,
        })
        
    elif report_type == 'profit':
        # Profit report
        sales = Transaction.objects.filter(
            transaction_type=TransactionType.STOCK_OUT,
            created_at__range=[start_date, end_date]
        )
        
        # Calculate profit (we need to join with product to get cost price)
        product_profits = []
        total_profit = 0
        
        for product in Product.objects.all():
            product_sales = sales.filter(product=product)
            if product_sales.exists():
                quantity_sold = product_sales.aggregate(total=Sum('quantity'))['total'] or 0
                sales_value = product_sales.aggregate(
                    total=Sum(F('quantity') * F('unit_price'))
                )['total'] or 0
                cost_value = quantity_sold * product.cost_price
                profit = sales_value - cost_value
                
                product_profits.append({
                    'product': product,
                    'quantity_sold': quantity_sold,
                    'sales_value': sales_value,
                    'cost_value': cost_value,
                    'profit': profit,
                    'margin': profit / sales_value * 100 if sales_value > 0 else 0,
                })
                
                total_profit += profit
        
        # Sort by profit
        product_profits.sort(key=lambda x: x['profit'], reverse=True)
        
        context.update({
            'product_profits': product_profits,
            'total_profit': total_profit,
        })
    
    return render(request, 'dashboard/reports.html', context)


@login_required
def update_preferences(request):
    """Update user dashboard preferences."""
    if request.method == 'POST':
        try:
            pref = request.user.dashboard_preference
        except:
            pref = DashboardPreference(user=request.user)
        
        pref.show_low_stock_first = request.POST.get('show_low_stock_first') == 'on'
        pref.items_per_page = int(request.POST.get('items_per_page', 20))
        pref.preferred_view = request.POST.get('preferred_view', 'list')
        pref.save()
    
    return redirect('dashboard:home')