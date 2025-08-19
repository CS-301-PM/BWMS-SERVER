# inventory/tests.py
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import StockItem, StockRequest

User = get_user_model()

class ManagerTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='testmanager',
            password='testpass123',
            user_type='MANAGER'
        )
        self.item = StockItem.objects.create(
            name="Test Item",
            quantity=10,
            location="Test Location"
        )
        self.request = StockRequest.objects.create(
            item=self.item,
            quantity=2,
            requester=self.manager,
            status='PENDING'
        )
        self.client.login(username='testmanager', password='testpass123')

    def test_request_approval(self):
        url = f'/api/stock-requests/{self.request.id}/'
        response = self.client.put(url, {'status': 'APPROVED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'APPROVED')

    def test_dashboard_access(self):
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_items', response.data)

    def test_stock_update(self):
        url = f'/api/stock-items/{self.item.id}/'
        response = self.client.put(url, {'quantity': 15})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 15)