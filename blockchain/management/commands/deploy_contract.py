from django.core.management.base import BaseCommand
from blockchain.web3_client import get_web3_client


class Command(BaseCommand):
    help = 'Deploys the StreamlinedStoresManager smart contract to the blockchain.'

    def handle(self, *args, **options):
        self.stdout.write('Initializing Web3 client and deploying contract...')
        try:
            client = get_web3_client()
            contract_address = client.deploy_contract()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deployed contract at address: {contract_address}')
            )
            self.stdout.write(
                self.style.WARNING('Please update the CONTRACT_ADDRESS variable in your .env file with the above address.')
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deploying contract: {e}'))