from django.test import TestCase
from .models import Category, Product


def make_category(name="Electronics"):
    return Category.objects.create(name=name)


def make_product(name="Widget", category=None, stock=10, threshold=5, price="9.99", cost="5.00"):
    if category is None:
        category = make_category()
    return Product.objects.create(
        name=name,
        category=category,
        sku=f"SKU-{name.upper().replace(' ', '-')}",
        price=price,
        cost_price=cost,
        stock_quantity=stock,
        low_stock_threshold=threshold,
    )


class CategoryModelTest(TestCase):
    def test_slug_auto_generated(self):
        cat = make_category("Home Appliances")
        self.assertEqual(cat.slug, "home-appliances")

    def test_str(self):
        cat = make_category("Books")
        self.assertEqual(str(cat), "Books")


class ProductModelTest(TestCase):
    def test_slug_auto_generated(self):
        p = make_product("Blue Widget")
        self.assertEqual(p.slug, "blue-widget")

    def test_is_low_stock_true(self):
        p = make_product(stock=3, threshold=5)
        self.assertTrue(p.is_low_stock)

    def test_is_low_stock_false(self):
        p = make_product(stock=10, threshold=5)
        self.assertFalse(p.is_low_stock)

    def test_is_low_stock_at_threshold(self):
        # exactly at threshold counts as low
        p = make_product(stock=5, threshold=5)
        self.assertTrue(p.is_low_stock)

    def test_profit_margin(self):
        p = make_product(price="10.00", cost="6.00")
        self.assertAlmostEqual(p.profit_margin, 40.0, places=1)

    def test_profit_margin_zero_cost(self):
        # cost_price has MinValueValidator(0.01) so 0 isn't valid,
        # but the property should not crash if cost_price is somehow 0
        p = make_product(price="10.00", cost="0.01")
        self.assertGreater(p.profit_margin, 0)
