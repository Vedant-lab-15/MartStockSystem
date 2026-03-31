from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import DashboardPreference

User = get_user_model()


class UpdatePreferencesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="prefuser", password="pass1234")
        self.client.force_login(self.user)  # bypass axes which needs a real request
        self.url = reverse('dashboard:preferences')

    def test_valid_items_per_page(self):
        self.client.post(self.url, {'items_per_page': '50', 'preferred_view': 'list'})
        pref = DashboardPreference.objects.get(user=self.user)
        self.assertEqual(pref.items_per_page, 50)

    def test_invalid_items_per_page_defaults_to_20(self):
        self.client.post(self.url, {'items_per_page': '999999', 'preferred_view': 'list'})
        pref = DashboardPreference.objects.get(user=self.user)
        self.assertEqual(pref.items_per_page, 20)

    def test_invalid_preferred_view_defaults_to_list(self):
        self.client.post(self.url, {'items_per_page': '20', 'preferred_view': 'hacked'})
        pref = DashboardPreference.objects.get(user=self.user)
        self.assertEqual(pref.preferred_view, 'list')

    def test_non_integer_items_per_page_defaults_to_20(self):
        self.client.post(self.url, {'items_per_page': 'abc', 'preferred_view': 'grid'})
        pref = DashboardPreference.objects.get(user=self.user)
        self.assertEqual(pref.items_per_page, 20)

    def test_unauthenticated_redirects(self):
        self.client.logout()
        response = self.client.post(self.url, {'items_per_page': '20'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])
