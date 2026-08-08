from web3 import Web3
from config import settings
import logging

logger = logging.getLogger(__name__)

# Connect to Sepolia testnet
w3 = Web3(Web3.HTTPProvider(settings.ETH_RPC_URL))

def verify_eth_transaction(tx_hash: str, expected_recipient: str, expected_amount_eth: float) -> bool:
    """
    Verifies that an Ethereum transaction hash:
    1. Exists and is mined successfully on-chain.
    2. Was sent to the expected recipient address.
    3. Contains at least the expected amount of ETH.
    """
    try:
        if not w3.is_connected():
            logger.error("Failed to connect to Ethereum RPC")
            return False

        # Wait for transaction receipt to ensure it's mined (max 30s timeout)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        
        # Status 1 means successful transaction
        if receipt.status != 1:
            logger.error(f"Transaction {tx_hash} failed on-chain")
            return False

        # Get the transaction details to verify amount and recipient
        tx = w3.eth.get_transaction(tx_hash)
        
        actual_recipient = tx.get('to')
        if not actual_recipient or actual_recipient.lower() != expected_recipient.lower():
            logger.error(f"Transaction {tx_hash} recipient mismatch. Expected {expected_recipient}, got {actual_recipient}")
            return False

        # Convert expected ETH to Wei for comparison
        expected_wei = w3.to_wei(expected_amount_eth, 'ether')
        actual_wei = tx.get('value', 0)

        # Allow slight overpayment but not underpayment
        if actual_wei < expected_wei:
            logger.error(f"Transaction {tx_hash} amount mismatch. Expected {expected_wei} wei, got {actual_wei} wei")
            return False

        return True

    except Exception as e:
        logger.error(f"Error verifying Ethereum transaction {tx_hash}: {str(e)}")
        return False
