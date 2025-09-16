import os
import json
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
from eth_account import Account
from hexbytes import HexBytes

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Web3Client:
    """
    A singleton client to interact with the StreamlinedStoresManagerV2 smart contract.
    Handles connection, transaction signing, and all contract function calls.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Web3Client, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._initialize()

    def _initialize(self):
        """Initialize the Web3 connection and contract."""
        self.rpc_url = os.getenv('BLOCKCHAIN_RPC_URL', 'http://127.0.0.1:8545') # Default to Ganache
        self.contract_address = os.getenv('CONTRACT_ADDRESS')
        self.private_key = os.getenv('DEPLOYER_PRIVATE_KEY') # Use a dedicated deployer/admin key

        # Check for simulation mode
        if not all([self.rpc_url, self.contract_address, self.private_key]):
            logger.warning("⚠️  Blockchain environment variables not fully set. Running in simulation mode.")
            self.simulation_mode = True
            return
        self.simulation_mode = False

        try:
            # Initialize Web3
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            # Add POA middleware if needed (e.g., for Ganache, BSC testnet)
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            if not self.w3.is_connected():
                raise ConnectionError(f"Failed to connect to Web3 provider at {self.rpc_url}")

            # Load contract ABI
            self.contract_abi = self._load_contract_abi()
            
            # Set up contract instance
            self.contract_address = Web3.to_checksum_address(self.contract_address)
            self.contract = self.w3.eth.contract(
                address=self.contract_address, 
                abi=self.contract_abi
            )

            # Set up account
            self.account = Account.from_key(self.private_key)
            logger.info(f"✅ Blockchain client initialized for account: {self.account.address}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Web3 client: {e}")
            self.simulation_mode = True # Fall back to simulation on error

    def _load_contract_abi(self):
        """Load the ABI from the compiled contract JSON file for V2."""
        try:
            contract_path = os.path.join(
                os.path.dirname(__file__), 
                'contracts', 
                'StreamlinedStoresManagerV2.json' # NOTE: We will compile this later
            )
            
            with open(contract_path, 'r') as f:
                contract_data = json.load(f)
                # Handle different compilation outputs (Truffle vs solcx)
                if 'abi' in contract_data:
                    return contract_data['abi']
                else:
                    raise KeyError("'abi' key not found in contract JSON file.")
                
        except FileNotFoundError:
            logger.error("Contract ABI file not found. Please compile StreamlinedStoresManagerV2.sol first.")
            raise
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing contract JSON: {e}")
            raise

    def _send_transaction(self, contract_function, *args):
        """
        Generic helper to build, sign, and send a transaction.
        Returns the transaction hash on success, None on failure.
        """
        if self.simulation_mode:
            simulated_tx_id = f"simulated_tx_{contract_function.fn_name}_{hash(str(args))}"
            logger.info(f"⚠️  Simulation Mode: {contract_function.fn_name} called with args {args}. Tx ID: {simulated_tx_id}")
            return simulated_tx_id

        try:
            # Build the transaction
            transaction = contract_function(*args).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 500000,  # Set a higher gas limit for more complex functions
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign the transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            
            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            # Wait for transaction receipt (optional, can be async)
            # receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            # logger.info(f"Transaction mined in block: {receipt.blockNumber}")
            
            logger.info(f"✅ {contract_function.fn_name} transaction sent: {tx_hash_hex}")
            return tx_hash_hex

        except Exception as e:
            logger.error(f"❌ Error sending transaction for {contract_function.fn_name}: {e}")
            return None

    # --- Public Methods for Contract Functions ---
    def log_approval(self, request_id, status, comment):
        """Log an approval decision. Status should be an integer matching the ApprovalStatus enum."""
        return self._send_transaction(self.contract.functions.logApproval, request_id, status, comment)

    def log_delivery(self, request_id, tracking_data):
        """Log a delivery. tracking_data could be a GRN number or supplier info."""
        return self._send_transaction(self.contract.functions.logDelivery, request_id, tracking_data)

    def log_relocation(self, item_id, from_location, to_location):
        """Log an item relocation."""
        return self._send_transaction(self.contract.functions.logRelocation, item_id, from_location, to_location)

    def report_damage(self, item_id, severity, details):
        """Report item damage. Severity should be an integer matching the DamageSeverity enum."""
        return self._send_transaction(self.contract.functions.reportDamage, item_id, severity, details)

    def assign_role(self, user_address, role):
        """Assign a role to a user address. Role should be an integer matching the Role enum."""
        return self._send_transaction(self.contract.functions.assignRole, Web3.to_checksum_address(user_address), role)

    # --- Event Listening (For future use with Celery) ---
    def get_delivery_events(self, from_block=0):
        """Get all DeliveryLogged events."""
        if self.simulation_mode:
            return []
        event_filter = self.contract.events.DeliveryLogged.create_filter(fromBlock=from_block)
        return event_filter.get_all_entries()

    # ... Similar getter functions for other events (RelocationLogged, DamageReportLogged) ...


# Global instance
web3_client = Web3Client()