from django.shortcuts import render, redirect
from .models import Product, Category, Transaction
from django.contrib import messages

def dashboard(request):
    products = Product.objects.all()
    low_stock = Product.objects.filter(stock__lte=5)
    return render(request, 'stock/dashboard.html', {
        'products': products,
        'low_stock': low_stock
    })

def add_transaction(request):
    if request.method == 'POST':
        product_id = request.POST['product']
        trans_type = request.POST['type']
        quantity = int(request.POST['quantity'])
        product = Product.objects.get(id=product_id)
        
        if trans_type == 'OUT' and product.stock < quantity:
            messages.error(request, f"Not enough stock for {product.name}!")
        else:
            Transaction.objects.create(product=product, type=trans_type, quantity=quantity)
            messages.success(request, f"Transaction recorded for {product.name}.")
        return redirect('dashboard')
    
    products = Product.objects.all()
    return render(request, 'stock/add_transaction.html', {'products': products})

# Create your views here.
