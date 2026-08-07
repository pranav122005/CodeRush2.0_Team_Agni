from pydantic import BaseModel
from typing import Optional

class X402PaymentPayload(BaseModel):
    payment_id: str
    transaction_id: str
    amount: float
    currency: str = "ALGO"
    scheme: str = "x402"
    network: str = "Algorand"
    recipient_address: str
    resource_identifier: str
    nonce: str
    # In a real app, signature validation is complex. For this, we assume a basic structure.
    signature: str 

class PaymentResponse(BaseModel):
    status: str
    receipt_id: Optional[str] = None
    message: str
