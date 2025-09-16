import os
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables
load_dotenv()

# Get values from .env
rpc_url = os.getenv('BLOCKCHAIN_RPC_URL')
private_key = os.getenv('STORE_MANAGER_PRIVATE_KEY')
contract_address = os.getenv('CONTRACT_ADDRESS')

print("=== Blockchain Configuration Test ===")
print(f"RPC URL: {rpc_url}")
print(f"Private Key: {private_key}")
print(f"Contract Address: {contract_address}")

# Test connection
try:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    print(f"Connected: {w3.is_connected()}")
    print(f"Latest block: {w3.eth.block_number}")
    
    # Test account
    if private_key:
        account = w3.eth.account.from_key(private_key)
        print(f"Account address: {account.address}")
        balance = w3.eth.get_balance(account.address)
        print(f"Account balance: {w3.from_wei(balance, 'ether')} ETH")
        
except Exception as e:
    print(f"Error: {e}")