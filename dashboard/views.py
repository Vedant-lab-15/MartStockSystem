from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta

from products.models import Product, Category
from transactions.models import Transaction, StockAlert, TransactionType
from .models import DashboardPreference

ITEMS_PER_PAGE_CHOICES = {10, 20, 50, 100}


@login_required
def dashboard_home(request):
    """Main dashboard view showing summary statistics and low stock items."""

    try:
        pref = request.user.dashboard_preference
    except Exception:
        pref = DashboardPreference(
            user=request.user,
            show_low_stock_first=True,
            items_per_page=20,
            preferred_view='list'
        )
        pref.save()

    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F('low_stock_threshold')
    )

    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_stock_value = Product.objects.aggregate(
        total=Sum(F('price') * F('stock_quantity'), output_field=DecimalField())
    )['total'] or 0

    today = timezone.now().date()
    today_transactions = Transaction.objects.filter(created_at__date=today)
    today_stock_in = today_transactions.filter(transaction_type=TransactionType.STOCK_IN)
    today_stock_out = today_transactions.filter(transaction_type=TransactionType.STOCK_OUT)
    today_stock_in_value = today_stock_in.aggregate(
        total=Sum(F('unit_price') * F('quantity'), output_field=DecimalField())
    )['total'] or 0
    today_stock_out_value = today_stock_out.aggregate(
        total=Sum(F('unit_price') * F('quantity'), output_field=DecimalField())
    )['total'] or 0

    recent_transactions = Transaction.objects.select_related('product').order_by('-created_at')[:10]
    unresolved_alerts = StockAlert.objects.filter(is_resolved=False).select_related('product')

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
    time_period = request.GET.get('period', '30')

    end_date = timezone.now()
    start_date = end_date - timedelta(days=int(time_period))

    context = {
        'report_type': report_type,
        'time_period': time_period,
        'start_date': start_date.date(),
        'end_date': end_date.date(),
    }

    if report_type == 'stock':
        context['categories'] = Category.objects.all()
        context['products'] = Product.objects.select_related('category').order_by('category__name', 'name')
        context['low_stock_count'] = Product.objects.filter(
            stock_quantity__lte=F('low_stock_threshold')
        ).count()

    elif report_type == 'sales':
        sales = Transaction.objects.filter(
            transaction_type=TransactionType.STOCK_OUT,
            created_at__range=[start_date, end_date]
        )

        daily_sales = sales.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            total_amount=Sum(F('quantity') * F('unit_price'), output_field=DecimalField()),
            count=Count('id')
        ).order_by('day')

        product_sales = sales.values('product__name').annotate(
            total_amount=Sum(F('quantity') * F('unit_price'), output_field=DecimalField()),
            count=Sum('quantity')
        ).order_by('-total_amount')

        category_sales = sales.values('product__category__name').annotate(
            total_amount=Sum(F('quantity') * F('unit_price'), output_field=DecimalField()),
            count=Sum('quantity')
        ).order_by('-total_amount')

        context.update({
            'daily_sales': daily_sales,
            'product_sales': product_sales,
            'category_sales': category_sales,
            'total_sales': sales.aggregate(
                total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
            )['total'] or 0,
        })

    elif report_type == 'profit':
        sales = Transaction.objects.filter(
            transaction_type=TransactionType.STOCK_OUT,
            created_at__range=[start_date, end_date]
        )

        product_profits_qs = sales.values(
            'product__id', 'product__name', 'product__cost_price'
        ).annotate(
            quantity_sold=Sum('quantity'),
            sales_value=Sum(F('quantity') * F('unit_price'), output_field=DecimalField()),
        ).order_by('-sales_value')

        product_profits = []
        total_profit = 0
        for row in product_profits_qs:
            cost_value = row['quantity_sold'] * row['product__cost_price']
            profit = row['sales_value'] - cost_value
            margin = float(profit) / float(row['sales_value']) * 100 if row['sales_value'] else 0
            product_profits.append({
                'product_name': row['product__name'],
                'quantity_sold': row['quantity_sold'],
                'sales_value': row['sales_value'],
                'cost_value': cost_value,
                'profit': profit,
                'margin': margin,
            })
            total_profit += profit

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
        except Exception:
            pref = DashboardPreference(user=request.user)

        pref.show_low_stock_first = request.POST.get('show_low_stock_first') == 'on'

        # Validate items_per_page against an allowlist to prevent abuse
        try:
            items_per_page = int(request.POST.get('items_per_page', 20))
        except (ValueError, TypeError):
            items_per_page = 20
        pref.items_per_page = items_per_page if items_per_page in ITEMS_PER_PAGE_CHOICES else 20

        preferred_view = request.POST.get('preferred_view', 'list')
        pref.preferred_view = preferred_view if preferred_view in ('list', 'grid') else 'list'

        pref.save()

    return redirect('dashboard:home')