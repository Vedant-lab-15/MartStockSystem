from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku']
    ordering_fields = ['name', 'price', 'stock_quantity', 'created_at']
    lookup_field = 'slug'

    def get_queryset(self):
        qs = Product.objects.select_related('category')
        if self.request.query_params.get('low_stock'):
            qs = qs.filter(stock_quantity__lte=F('low_stock_threshold'))
        if self.request.query_params.get('category'):
            qs = qs.filter(category__slug=self.request.query_params['category'])
        return qs
