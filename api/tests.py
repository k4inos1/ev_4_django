from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Company, Equipment, Technician, MaintenancePlan, WorkOrder
from datetime import date

class MaintenanceSystemTests(TestCase):
    def setUp(self):
        # Users
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'pass')
        self.regular_user = User.objects.create_user('user', 'user@example.com', 'pass')
        
        # Clients
        self.client = APIClient()
        
        # Data
        self.company = Company.objects.create(name="Test Co", address="123 St", rut="11.111.111-1")
        self.equipment = Equipment.objects.create(
            company=self.company, name="Drill", serial_number="D100", 
            critical=True, installed_at=date(2023, 1, 1)
        )
        self.tech = Technician.objects.create(
            user=self.admin_user, full_name="Bob Builder", specialty="Fixer", phone="555-1234"
        )
        self.plan = MaintenancePlan.objects.create(
            equipment=self.equipment, name="Yearly Check", frequency_days=365
        )

    def test_company_creation_permission(self):
        # Unauthenticated -> 401
        self.client.logout()
        response = self.client.post('/api/companies/', {'name': 'New Co', 'address': 'A', 'rut': '2'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated -> 201
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post('/api/companies/', {'name': 'New Co', 'address': 'A', 'rut': '2'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_work_order_signal(self):
        # Create work order
        wo = WorkOrder.objects.create(
            plan=self.plan, equipment=self.equipment, technician=self.tech,
            status='PENDING', scheduled_date=date(2025, 1, 1)
        )
        self.assertIsNone(wo.completed_at)

        # Update status to COMPLETED
        wo.status = 'COMPLETED'
        wo.save()
        
        # Refresh and check signal
        wo.refresh_from_db()
        self.assertIsNotNone(wo.completed_at)

    def test_filtering(self):
        # Add another company
        Company.objects.create(name="Another Corp", address="456 Rd", rut="22.222.222-2")
        
        self.client.force_authenticate(user=self.regular_user)
        
        # Filter by RUT
        response = self.client.get(f'/api/companies/?rut={self.company.rut}')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Co")

        # Search
        response = self.client.get('/api/companies/?search=Another')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Another Corp")
