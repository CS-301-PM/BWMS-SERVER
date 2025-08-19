import json
import os
from web3 import Web3
from django.conf import settings

class BlockchainLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
            
            contract_path = os.path.join(
                settings.BASE_DIR.parent,
                'blockchain/artifacts/contracts/InventoryLedger.sol/InventoryLedger.json'
            )
            
            with open(contract_path) as f:
                contract_data = json.load(f)
                
            cls._instance.contract = cls._instance.w3.eth.contract(
                address="0x5FbDB2315678afecb367f032d93F642f64180aa3",  # Hardhat default
                abi=contract_data['abi']
            )
            
            # Use the first Hardhat test account
            cls._instance.account = cls._instance.w3.eth.accounts[0]
        return cls._instance

    def log_approval(self, request_id, item_id, quantity):
        tx_hash = self.contract.functions.logRequestApproval(
            request_id,
            str(item_id),
            int(quantity)
        ).transact({'from': self.account})
        return tx_hash.hex()

    def log_stock_update(self, item_id, new_quantity, action_type):
        tx_hash = self.contract.functions.logStockUpdate(
            str(item_id),
            int(new_quantity),
            action_type
        ).transact({'from': self.account})
        return tx_hash.hex()

class BlockchainService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
            
            # Load contract ABI
            contract_path = os.path.join(
                settings.BASE_DIR.parent, 
                'blockchain/artifacts/contracts/InventoryLedger.sol/InventoryLedger.json'
            )
            
            with open(contract_path) as f:
                contract_data = json.load(f)
            
            cls._instance.contract = cls._instance.w3.eth.contract(
                address=settings.CONTRACT_ADDRESS,
                abi=contract_data['abi']
            )
        return cls._instance
    
    def log_transaction(self, user, item_id, quantity, action_type):
        if not user.wallet_address:
            raise ValueError("User has no wallet address configured")
            
        tx = self.contract.functions.logAction(
            item_id,
            quantity,
            action_type
        ).build_transaction({
            'from': user.wallet_address,
            'nonce': self.w3.eth.get_transaction_count(user.wallet_address),
            'gas': 2000000
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, settings.PRIVATE_KEY)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()