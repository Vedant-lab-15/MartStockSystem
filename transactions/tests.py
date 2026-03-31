from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Category, Product
from .models import Transaction, TransactionType, StockAlert

User = get_user_model()
_user_counter = 0


def make_product(name="Widget", stock=20):
    cat = Category.objects.create(name=f"Cat-{name}")
    return Product.objects.create(
        name=name,
        category=cat,
        sku=f"SKU-{name.upper()}",
        price="10.00",
        cost_price="6.00",
        stock_quantity=stock,
        low_stock_threshold=5,
    )


def make_user():
    global _user_counter
    _user_counter += 1
    return User.objects.create_user(username=f"user{_user_counter}", password="pass1234")


class StockInTest(TestCase):
    def test_stock_in_increases_quantity(self):
        product = make_product(stock=10)
        Transaction.objects.create(
            product=product,
            quantity=5,
            transaction_type=TransactionType.STOCK_IN,
            unit_price="6.00",
            created_by=make_user(),
        )
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 15)


class StockOutTest(TestCase):
    def test_stock_out_decreases_quantity(self):
        product = make_product(stock=10)
        Transaction.objects.create(
            product=product,
            quantity=4,
            transaction_type=TransactionType.STOCK_OUT,
            unit_price="10.00",
            created_by=make_user(),
        )
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 6)

    def test_stock_out_cannot_go_below_zero(self):
        # The DB PositiveIntegerField constraint prevents going negative.
        # In practice StockOutForm validates this first; at the model level
        # attempting to overdraw raises IntegrityError.
        from django.db import IntegrityError
        product = make_product(stock=3)
        with self.assertRaises(IntegrityError):
            Transaction.objects.create(
                product=product,
                quantity=10,
                transaction_type=TransactionType.STOCK_OUT,
                unit_price="10.00",
                created_by=make_user(),
            )


class AdjustmentTest(TestCase):
    def test_adjustment_increase(self):
        product = make_product(stock=10)
        Transaction.objects.create(
            product=product,
            quantity=5,
            transaction_type=TransactionType.ADJUSTMENT_INCREASE,
            unit_price="6.00",
            created_by=make_user(),
        )
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 15)

    def test_adjustment_decrease(self):
        product = make_product(stock=10)
        Transaction.objects.create(
            product=product,
            quantity=3,
            transaction_type=TransactionType.ADJUSTMENT_DECREASE,
            unit_price="6.00",
            created_by=make_user(),
        )
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 7)


class StockAlertSignalTest(TestCase):
    def test_alert_created_when_low_stock(self):
        product = make_product(stock=10, name="LowItem")
        # Manually drop stock below threshold to trigger signal
        product.stock_quantity = 2
        product.save()
        self.assertTrue(StockAlert.objects.filter(product=product, is_resolved=False).exists())

    def test_no_duplicate_alert(self):
        product = make_product(stock=10, name="DupItem")
        product.stock_quantity = 2
        product.save()
        product.save()  # save again — should not create a second alert
        self.assertEqual(StockAlert.objects.filter(product=product, is_resolved=False).count(), 1)
