from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Sum, Count, F
from django.utils import timezone

from .models import Transaction, StockAlert, TransactionType
from .forms import StockInForm, StockOutForm, StockAdjustmentForm, StockAlertForm
from products.models import Product


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by product if provided in GET parameters
        product_id = self.request.GET.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
            
        # Filter by transaction type if provided
        transaction_type = self.request.GET.get('type')
        if transaction_type and transaction_type in dict(TransactionType.choices).keys():
            queryset = queryset.filter(transaction_type=transaction_type)
            
        # Filter by date range if provided
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['transaction_types'] = TransactionType.choices
        
        # Add filter parameters to context
        context['product_id'] = self.request.GET.get('product', '')
        context['transaction_type'] = self.request.GET.get('type', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'


class StockInCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Transaction
    form_class = StockInForm
    template_name = 'transactions/stock_in_form.html'
    permission_required = 'transactions.add_transaction'
    success_url = reverse_lazy('transactions:transaction_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Stock added successfully!")
        return super().form_valid(form)


class StockOutCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Transaction
    form_class = StockOutForm
    template_name = 'transactions/stock_out_form.html'
    permission_required = 'transactions.add_transaction'
    success_url = reverse_lazy('transactions:transaction_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Stock out transaction recorded successfully!")
        return super().form_valid(form)


class StockAdjustmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Transaction
    form_class = StockAdjustmentForm
    template_name = 'transactions/stock_adjustment_form.html'
    permission_required = 'transactions.add_transaction'
    success_url = reverse_lazy('transactions:transaction_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Stock adjustment recorded successfully!")
        return super().form_valid(form)


class StockAlertListView(LoginRequiredMixin, ListView):
    model = StockAlert
    template_name = 'transactions/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by resolved status if provided
        status = self.request.GET.get('status')
        if status == 'resolved':
            queryset = queryset.filter(is_resolved=True)
        elif status == 'unresolved':
            queryset = queryset.filter(is_resolved=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', '')
        return context


@login_required
@permission_required('transactions.change_stockalert')
def resolve_alert(request, pk):
    alert = get_object_or_404(StockAlert, pk=pk)
    alert.is_resolved = True
    alert.resolved_at = timezone.now()
    alert.save()
    messages.success(request, "Alert marked as resolved.")
    return redirect('transactions:alert_list')