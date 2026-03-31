from rest_framework.routers import DefaultRouter
from products.api_views import CategoryViewSet, ProductViewSet
from transactions.api_views import TransactionViewSet, StockAlertViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('transactions', TransactionViewSet, basename='transaction')
router.register('alerts', StockAlertViewSet, basename='alert')

urlpatterns = router.urls
