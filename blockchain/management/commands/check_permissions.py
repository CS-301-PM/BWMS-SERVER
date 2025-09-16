from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from procurement_requests.models import DepartmentRequest

User = get_user_model()

class Command(BaseCommand):
    help = 'Check user permissions for viewing requests'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Checking user permissions...')
        
        # Get users
        try:
            stores_manager = User.objects.get(username='stores_manager1')
            dean = User.objects.get(username='dean_ict1')
            
            # Get some requests
            requests = DepartmentRequest.objects.all()[:5]
            
            self.stdout.write(f"\nStores Manager: {stores_manager.username} ({stores_manager.role})")
            self.stdout.write(f"Department Dean: {dean.username} ({dean.role})")
            self.stdout.write(f"Total requests: {DepartmentRequest.objects.count()}")
            
            # Check what each user can see
            self.stdout.write(f"\n📊 Requests visible to Stores Manager:")
            stores_requests = DepartmentRequest.objects.all()
            for req in stores_requests:
                self.stdout.write(f"  - Request #{req.id}: {req.product.name} by {req.requested_by.username} - Status: {req.status}")
            
            self.stdout.write(f"\n📊 Requests visible to Dean:")
            dean_requests = DepartmentRequest.objects.filter(requested_by=dean)
            for req in dean_requests:
                self.stdout.write(f"  - Request #{req.id}: {req.product.name} - Status: {req.status}")
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Test users not found. Run create_initial_users first.'))