from django import forms
from .models import Transaction, StockAlert
from products.models import Product


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['product', 'quantity', 'transaction_type', 'unit_price', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter out products that are not active
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        # Display product name and SKU in dropdown
        self.fields['product'].label_from_instance = lambda obj: f"{obj.name} (SKU: {obj.sku})"


class StockInForm(TransactionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].initial = 'IN'
        self.fields['transaction_type'].widget = forms.HiddenInput()
        self.fields['unit_price'].label = 'Cost Price Per Unit'


class StockOutForm(TransactionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].initial = 'OUT'
        self.fields['transaction_type'].widget = forms.HiddenInput()
        self.fields['unit_price'].label = 'Selling Price Per Unit'
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        
        if product and quantity:
            # Check if enough stock is available
            if product.stock_quantity < quantity:
                raise forms.ValidationError(
                    f"Not enough stock available. Current stock: {product.stock_quantity}"
                )
        
        return cleaned_data


class StockAdjustmentForm(TransactionForm):
    adjustment_type = forms.ChoiceField(
        choices=[
            ('increase', 'Increase Stock'),
            ('decrease', 'Decrease Stock'),
        ],
        initial='increase',
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].initial = 'ADJ'
        self.fields['transaction_type'].widget = forms.HiddenInput()
        self.fields['unit_price'].label = 'Value Per Unit'
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        adjustment_type = cleaned_data.get('adjustment_type')
        
        if product and quantity and adjustment_type == 'decrease':
            # Check if enough stock is available for decrease
            if product.stock_quantity < quantity:
                raise forms.ValidationError(
                    f"Not enough stock available for decrease. Current stock: {product.stock_quantity}"
                )
                
        # Add adjustment type to notes
        notes = cleaned_data.get('notes', '')
        adjustment_note = f"Stock {adjustment_type}: "
        if not notes.startswith(adjustment_note):
            cleaned_data['notes'] = adjustment_note + notes
            
        return cleaned_data


class StockAlertForm(forms.ModelForm):
    class Meta:
        model = StockAlert
        fields = ['product', 'message', 'is_resolved']