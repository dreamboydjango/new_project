from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from marketplace.models import Product, Order, OrderItem, Category
from django.utils import timezone


class DashboardPageTests(TestCase):
    def setUp(self):
        # seller and buyer accounts
        self.seller = User.objects.create_user(
            username='seller1',
            email='seller@example.com',
            password='password123',
            role=User.SELLER
        )
        self.buyer = User.objects.create_user(
            username='buyer1',
            email='buyer@example.com',
            password='password123',
            role=User.BUYER
        )
        # a category and product
        self.category = Category.objects.create(name='Test Cat', slug='test-cat')
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name='Widget',
            description='A test widget',
            price=10.00,
            stock=3,  # low stock
        )
        # an order and item
        self.order = Order.objects.create(buyer=self.buyer, status='CONFIRMED')
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, price=20.00)

        self.client.login(username='seller1', password='password123')

    def assertDashboardGets(self, url_name):
        response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, 200)
        # page should include sidebar markup (at least the word 'sidebar')
        self.assertContains(response, 'sidebar')

    def test_seller_dashboard_view(self):
        resp = self.client.get(reverse('dashboard:seller_dashboard'))
        self.assertContains(resp, 'Total Revenue')
        self.assertContains(resp, 'Widget')

    def test_orders_view(self):
        resp = self.client.get(reverse('dashboard:orders'))
        self.assertContains(resp, '#%d' % self.order.id)
        # page lists buyer username and revenue
        self.assertContains(resp, 'buyer1')
        self.assertContains(resp, '$20')

    def test_analytics_view(self):
        resp = self.client.get(reverse('dashboard:analytics'))
        self.assertContains(resp, 'Revenue by Month')
        # chart data should include our price value
        self.assertContains(resp, '20.0')

    def test_insights_view(self):
        resp = self.client.get(reverse('dashboard:insights'))
        self.assertContains(resp, 'Low stock products')
        self.assertContains(resp, 'Widget')
