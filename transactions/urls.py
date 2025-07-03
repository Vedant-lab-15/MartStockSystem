from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Transaction URLs
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('stock-in/', views.StockInCreateView.as_view(), name='stock_in'),
    path('stock-out/', views.StockOutCreateView.as_view(), name='stock_out'),
    path('adjustment/', views.StockAdjustmentCreateView.as_view(), name='stock_adjustment'),
    
    # Stock Alert URLs
    path('alerts/', views.StockAlertListView.as_view(), name='alert_list'),
    path('alerts/<int:pk>/resolve/', views.resolve_alert, name='resolve_alert'),
]