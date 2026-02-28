from django.test import TestCase
from django.urls import reverse
from accounts.models import User


class HomePageTests(TestCase):
    def test_start_selling_link_anonymous(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'href="%s"' % reverse('accounts:signup'))

    def test_start_selling_link_logged_in_seller(self):
        user = User.objects.create_user(username='test', password='pw', role=User.SELLER)
        self.client.login(username='test', password='pw')
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'href="%s"' % reverse('dashboard:seller_dashboard'))

    def test_start_selling_not_shown_for_buyer(self):
        buyer = User.objects.create_user(username='b', password='pw', role=User.BUYER)
        self.client.login(username='b', password='pw')
        resp = self.client.get(reverse('core:home'))
        # should not contain either signup or seller dashboard link
        self.assertNotContains(resp, reverse('dashboard:seller_dashboard'))
        self.assertNotContains(resp, reverse('accounts:signup'))

    def test_login_page_hides_signup_link_if_logged_in(self):
        user = User.objects.create_user(username='u', password='pw', role=User.BUYER)
        self.client.login(username='u', password='pw')
        resp = self.client.get(reverse('accounts:login'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Sign Up')
