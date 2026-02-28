from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from marketplace.models import Category


class CategoryAdminTests(TestCase):
    def setUp(self):
        # create and login as administrator
        self.admin = User.objects.create_user(username='admin', password='pass', role=User.ADMIN)
        self.client.login(username='admin', password='pass')

    def test_category_list_shows_entries(self):
        Category.objects.create(name='cat1')
        response = self.client.get(reverse('adminpanel:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cat1')

    def test_category_create(self):
        response = self.client.post(reverse('adminpanel:category_add'), {'name': 'new', 'description': 'desc'})
        self.assertRedirects(response, reverse('adminpanel:category_list'))
        self.assertTrue(Category.objects.filter(name='new').exists())

    def test_category_update(self):
        cat = Category.objects.create(name='old')
        response = self.client.post(reverse('adminpanel:category_edit', args=[cat.pk]),
                                    {'name': 'updated', 'description': 'hello'})
        self.assertRedirects(response, reverse('adminpanel:category_list'))
        cat.refresh_from_db()
        self.assertEqual(cat.name, 'updated')

    def test_category_delete(self):
        cat = Category.objects.create(name='todel')
        response = self.client.post(reverse('adminpanel:category_delete', args=[cat.pk]))
        self.assertRedirects(response, reverse('adminpanel:category_list'))
        self.assertFalse(Category.objects.filter(pk=cat.pk).exists())

    def test_non_admin_cannot_access(self):
        self.client.logout()
        buyer = User.objects.create_user(username='buyer', password='pass', role=User.BUYER)
        self.client.login(username='buyer', password='pass')
        resp = self.client.get(reverse('adminpanel:category_list'))
        # because UserPassesTestMixin handle_no_permission simply redirects to login without
        # preserving `next`, we expect a plain login redirect.
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('accounts:login'))

    def test_dashboard_includes_category_count(self):
        Category.objects.create(name='one')
        response = self.client.get(reverse('adminpanel:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_categories'], 1)

    def test_order_list_displays_id_and_total(self):
        # prepare product and order with items
        buyer = User.objects.create_user(username='buyer2', password='pw', role=User.BUYER)
        product = Category.objects.create(name='temp')  # use category to create product later
        # create actual product using seller=admin
        from marketplace.models import Product, Order, OrderItem
        prod = Product.objects.create(seller=self.admin, category=product, name='X', description='', price=10, stock=5)
        order = Order.objects.create(buyer=buyer)
        OrderItem.objects.create(order=order, product=prod, quantity=2, price=10)

        response = self.client.get(reverse('adminpanel:order_list'))
        self.assertContains(response, f'#{order.id}')
        # annotation now multiplies quantity
        self.assertContains(response, '$20')
