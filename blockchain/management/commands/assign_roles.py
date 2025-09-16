from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blockchain.utils import BlockchainUtils

User = get_user_model()

class Command(BaseCommand):
    help = 'Assign blockchain roles using Ganache accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ganache',
            action='store_true',
            help='Use Ganache test accounts for role assignment'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting blockchain role assignment...')
        
        # Ganache test accounts (first 5 accounts from Ganache CLI)
        GANACHE_ACCOUNTS = [
            "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1",  # Account 1 - Stores Manager
            "0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0",  # Account 2 - Procurement Officer  
            "0x22d491Bde2303f2f43325b2108D26f1eAb1e6c12",  # Account 3 - CFO
            "0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d",  # Account 4 - Department Dean
            "0xd03ea8624C8C5987235048901fB614fDcA89b117"   # Account 5 - Admin
        ]
        
        ROLE_ASSIGNMENTS = {
            'STORES_MANAGER': GANACHE_ACCOUNTS[0],
            'PROCUREMENT_OFFICER': GANACHE_ACCOUNTS[1],
            'CFO': GANACHE_ACCOUNTS[2], 
            'DEPARTMENT_DEAN': GANACHE_ACCOUNTS[3],
            'ADMIN': GANACHE_ACCOUNTS[4]
        }

        if options['ganache']:
            self.stdout.write('📋 Using Ganache test accounts for role assignment...')
            
            for role_name, blockchain_address in ROLE_ASSIGNMENTS.items():
                try:
                    # Find or create user for this role
                    user, created = User.objects.get_or_create(
                        username=f'{role_name.lower()}_ganache',
                        defaults={
                            'email': f'{role_name.lower()}@cbu.edu.zm',
                            'role': role_name,
                            'blockchain_address': blockchain_address,
                            'password': 'testpass123'  # Default password
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'✅ Created user: {user.username}'))
                    
                    # Assign role on blockchain
                    self.stdout.write(f'🔗 Assigning {role_name} role to {blockchain_address}...')
                    tx_hash = BlockchainUtils.assign_role_on_blockchain(blockchain_address, role_name)
                    self.stdout.write(self.style.SUCCESS(f'   ✅ Success! Transaction: {tx_hash}'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Failed: {e}'))
        
        else:
            # Original functionality - assign to existing users
            self.stdout.write('👥 Assigning roles to existing users...')
            approvers = User.objects.exclude(role__in=[User.Role.DEPARTMENT_DEAN, User.Role.ADMIN])

            for user in approvers:
                if user.blockchain_address:
                    self.stdout.write(f'🔗 Assigning role {user.role} to {user.blockchain_address}...')
                    try:
                        tx_hash = BlockchainUtils.assign_role_on_blockchain(user.blockchain_address, user.role)
                        self.stdout.write(self.style.SUCCESS(f'   ✅ Success! Transaction: {tx_hash}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'   ❌ Failed: {e}'))
                else:
                    self.stdout.write(self.style.WARNING(f'   ⚠️ Skipping {user.username}: No blockchain address'))

        self.stdout.write(self.style.SUCCESS('🎉 Role assignment process finished!'))