import hmac
import hashlib
import json
import time
from app.config import settings

class ReceiptService:
    @staticmethod
    def issue_receipt(payment_id: str, trace_id: str, network: str, tx_hash: str, amount: str, recipient: str) -> dict:
        receipt_data = {
            "receipt_id": f"rcpt_{payment_id}",
            "payment_id": payment_id,
            "trace_id": trace_id,
            "verification_status": "VERIFIED",
            "settlement_status": "SETTLED",
            "tx_hash": tx_hash,
            "network": network,
            "amount": amount,
            "recipient": recipient,
            "timestamp": int(time.time()),
        }
        
        serialized = json.dumps(receipt_data, sort_keys=True)
        signature = hmac.new(settings.SECRET_KEY, serialized.encode('utf-8'), hashlib.sha256).hexdigest()
        receipt_data["signature"] = signature
        return receipt_data

    @staticmethod
    def verify_receipt(receipt: dict) -> bool:
        signature = receipt.get("signature")
        if not signature:
            return False
        
        payload = {k: v for k, v in receipt.items() if k != "signature"}
        serialized = json.dumps(payload, sort_keys=True)
        expected = hmac.new(settings.SECRET_KEY, serialized.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)

receipt_service = ReceiptService()
