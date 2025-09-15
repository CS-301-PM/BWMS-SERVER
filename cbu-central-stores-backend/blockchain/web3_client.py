import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Web3Client:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Web3Client, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize only when first used, not at import time."""
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self):
        """Initialize the Web3 connection and load the actual contract."""
        self.rpc_url = os.getenv('BLOCKCHAIN_RPC_URL')
        self.contract_address = os.getenv('CONTRACT_ADDRESS')
        self.private_key = os.getenv('STORE_MANAGER_PRIVATE_KEY')

        # Check if we're in development mode without blockchain config
        if not all([self.rpc_url, self.contract_address, self.private_key]):
            print("⚠️  Blockchain environment variables not set. Running in simulation mode.")
            self.simulation_mode = True
            return

        self.simulation_mode = False

        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Check connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Web3 provider at {self.rpc_url}")

        # Load contract ABI from compiled JSON file
        self.contract_abi = self._load_contract_abi()
        
        # Set up contract instance
        self.contract_address = Web3.to_checksum_address(self.contract_address)
        self.contract = self.w3.eth.contract(
            address=self.contract_address, 
            abi=self.contract_abi
        )

        # Get the account from private key
        self.account = self.w3.eth.account.from_key(self.private_key)
        print("✅ Blockchain client initialized successfully")

    def _load_contract_abi(self):
        """Load the ABI from the compiled contract JSON file."""
        try:
            contract_path = os.path.join(
                os.path.dirname(__file__), 
                'contracts', 
                'StreamlinedStoresManager.json'
            )
            
            with open(contract_path, 'r') as f:
                contract_data = json.load(f)
                return contract_data['abi']
                
        except FileNotFoundError:
            raise FileNotFoundError("Contract ABI file not found. Please ensure StreamlinedStoresManager.json exists in blockchain/contracts/")
        except KeyError:
            raise KeyError("ABI not found in contract JSON file")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in contract file")

    def log_approval(self, request_id, stage, approver_role, approver_address, approved, comment):
        """
        Send a transaction to the blockchain to log an approval decision.
        Returns the transaction hash if successful.
        """
        if self.simulation_mode:
            print("⚠️  Blockchain simulation mode: Approval not logged to chain")
            return f"simulated_tx_{request_id}_{stage}"

        try:
            # Build the transaction
            transaction = self.contract.functions.logApproval(
                request_id,
                stage,
                approver_role,
                Web3.to_checksum_address(approver_address),
                approved,
                comment[:100]  # Trim to avoid gas limits
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign the transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            
            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transation_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Blockchain log successful! Tx Hash: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                print(f"❌ Transaction failed: {receipt}")
                return None

        except Exception as e:
            print(f"Error logging approval to blockchain: {e}")
            return None

    def get_approval_events(self, request_id=None):
        """Retrieve approval events from the blockchain."""
        if self.simulation_mode:
            return []

        event_filter = self.contract.events.ApprovalLogged.create_filter(
            fromBlock=0
        )
        
        events = event_filter.get_all_entries()
        
        if request_id is not None:
            events = [e for e in events if e['args']['requestId'] == request_id]
            
        return events
    

# Create instance but don't initialize until first use
web3_client = Web3Client()