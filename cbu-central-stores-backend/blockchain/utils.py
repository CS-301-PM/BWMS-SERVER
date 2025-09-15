import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

class BlockchainUtils:
    @staticmethod
    def get_web3_client():
        """Get configured Web3 client"""
        from .web3_client import web3_client
        return web3_client

    @staticmethod
    def assign_role_on_blockchain(user_address, role):
        """
        Assign a role to a user on the blockchain
        Returns transaction hash
        """
        try:
            web3_client = BlockchainUtils.get_web3_client()
            
            # Map Django roles to blockchain role identifiers
            role_mapping = {
                'STORES_MANAGER': 'STORES_MANAGER',
                'PROCUREMENT_OFFICER': 'PROCUREMENT_OFFICER', 
                'CFO': 'CFO',
                'DEPARTMENT_DEAN': 'DEPARTMENT_DEAN',
                'ADMIN': 'ADMIN'
            }
            
            blockchain_role = role_mapping.get(role, '')
            if not blockchain_role:
                raise ValueError(f"Unknown role: {role}")
            
            # Build transaction to assign role
            transaction = web3_client.contract.functions.assignRole(
                Web3.to_checksum_address(user_address),
                blockchain_role
            ).build_transaction({
                'from': web3_client.account.address,
                'nonce': web3_client.w3.eth.get_transaction_count(web3_client.account.address),
                'gas': 200000,
                'gasPrice': web3_client.w3.eth.gas_price
            })

            # Sign and send transaction
            signed_txn = web3_client.w3.eth.account.sign_transaction(
                transaction, 
                private_key=web3_client.private_key
            )
            
            tx_hash = web3_client.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = web3_client.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return tx_hash.hex()
            else:
                raise Exception("Transaction failed")
                
        except Exception as e:
            print(f"Error assigning role on blockchain: {e}")
            raise