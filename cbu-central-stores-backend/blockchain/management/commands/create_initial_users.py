from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial test users with Ganache addresses'

    def handle(self, *args, **options):
        users_data = [
            {
                'username': 'stores_manager1',
                'email': 'stores@cbu.edu.zm',
                'role': User.Role.STORES_MANAGER,
                'blockchain_address': '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1',
                'password': 'testpass123'
            },
            {
                'username': 'procurement1', 
                'email': 'procurement@cbu.edu.zm',
                'role': User.Role.PROCUREMENT_OFFICER,
                'blockchain_address': '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0',
                'password': 'testpass123'
            },
            {
                'username': 'cfo1',
                'email': 'cfo@cbu.edu.zm', 
                'role': User.Role.CFO,
                'blockchain_address': '0x22d491Bde2303f2f43325b2108D26f1eAb1e6c12',
                'password': 'testpass123'
            },
            {
                'username': 'dean_ict1',
                'email': 'dean.ict@cbu.edu.zm',
                'role': User.Role.DEPARTMENT_DEAN,
                'blockchain_address': '0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d',
                'password': 'testpass123'
            },
            {
                'username': 'admin1',
                'email': 'admin@cbu.edu.zm',
                'role': User.Role.ADMIN,
                'blockchain_address': '0xd03ea8624C8C5987235048901fB614fDcA89b117',
                'password': 'testpass123'
            }
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User already exists: {user.username}'))