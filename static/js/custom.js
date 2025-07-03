// Custom JavaScript for Stock Management System

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // Product form - Update cost price when price changes
    const priceInput = document.getElementById('id_price');
    const costPriceInput = document.getElementById('id_cost_price');
    
    if (priceInput && costPriceInput) {
        // Only for new products (if both fields are empty)
        if (priceInput.value === '' && costPriceInput.value === '') {
            priceInput.addEventListener('input', function() {
                // Set default cost price to 80% of price
                const price = parseFloat(priceInput.value);
                if (!isNaN(price)) {
                    costPriceInput.value = (price * 0.8).toFixed(2);
                }
            });
        }
    }
    
    // Transaction forms - Update unit price when product changes
    const productSelect = document.getElementById('id_product');
    const unitPriceInput = document.getElementById('id_unit_price');
    
    if (productSelect && unitPriceInput) {
        // This would require an AJAX call to get the product price
        // In a real application, you would implement this
        // For demonstration purposes, we'll leave this as a placeholder
    }
});