from sqlalchemy.orm import Session
from models import PaymentRecord, Receipt
from schemas import X402PaymentPayload
from services.receipt import generate_pdf_receipt

import httpx

NEXUS_MESH_URL = "http://localhost:8001/api/v1"


def process_payment(payload: X402PaymentPayload, db: Session):
    # 1. Local Idempotency Check
    existing = db.query(PaymentRecord).filter(PaymentRecord.payment_id == payload.payment_id).first()
    if existing:
        return {"status": "failed", "message": "Duplicate payment_id detected."}
        
    existing_tx = db.query(PaymentRecord).filter(PaymentRecord.transaction_id == payload.transaction_id).first()
    if existing_tx:
         return {"status": "failed", "message": "Duplicate transaction_id detected."}

    # 2. Save pending state
    payment_record = PaymentRecord(
        payment_id=payload.payment_id,
        transaction_id=payload.transaction_id,
        amount=payload.amount,
        currency=payload.currency,
        resource_identifier=payload.resource_identifier,
        status="pending"
    )
    db.add(payment_record)
    db.commit()
    
    # Map currency to CAIP-2 network identifier
    network_map = {
        "ALGO": "algorand:testnet",
        "USDC": "algorand:testnet",   # USDC is an ASA on Algorand Testnet
        "ETH":  "ethereum:sepolia",
        "SOL":  "solana:devnet"
    }
    network_id = network_map.get(payload.currency, "algorand:testnet")

    # 3. Call NEXUS Mesh to Verify & Settle
    try:
        # Timeout is 90s to accommodate real Algorand testnet confirmation (~4-8 rounds)
        with httpx.Client(timeout=90.0) as client:
            # 3a. Verify with NEXUS Mesh
            verify_res = client.post(f"{NEXUS_MESH_URL}/verify", json={
                "payment_header": payload.signature if payload.signature != "mock_signature" else f'{{"scheme":"exact","network":"{network_id}","payload":{{"payment_id":"{payload.payment_id}","transaction_id":"{payload.transaction_id}"}},"resource_url":"{payload.resource_identifier}"}}',
                "requirement": {
                    "scheme": "exact",
                    "price": f"${payload.amount}",
                    "network": network_id,
                    "payTo": payload.recipient_address,
                    "asset_id": "10458941"
                }
            })
            
            if verify_res.status_code != 200:
                payment_record.status = "failed"
                db.commit()
                detail = verify_res.json().get("detail", "Verification failed at NEXUS Mesh")
                return {"status": "failed", "message": detail}

            verify_data = verify_res.json()
            trace_id = verify_data["trace_id"]

            # 3b. Settle with NEXUS Mesh
            settle_res = client.post(f"{NEXUS_MESH_URL}/settle", json={
                "trace_id": trace_id,
                "payment_header": payload.signature if payload.signature != "mock_signature" else f'{{"scheme":"exact","network":"{network_id}","payload":{{"payment_id":"{payload.payment_id}","transaction_id":"{payload.transaction_id}"}},"resource_url":"{payload.resource_identifier}"}}'
            })

            if settle_res.status_code != 200:
                payment_record.status = "failed"
                db.commit()
                return {"status": "failed", "message": "Settlement failed at NEXUS Mesh"}

            settle_data = settle_res.json()
            
            # 4. Settlement Succeeded
            payment_record.status = "succeeded"
            db.commit()
            
            # 5. Generate Receipt PDF locally & save
            receipt_id = generate_pdf_receipt(
                payload.payment_id, payload.transaction_id, payload.amount, payload.currency, payload.resource_identifier
            )
            
            db_receipt = Receipt(
                receipt_id=receipt_id,
                payment_id=payload.payment_id,
                file_path=f"receipts/{receipt_id}.pdf"
            )
            db.add(db_receipt)
            db.commit()
            
            return {
                "status": "success", 
                "message": "Payment settled successfully via NEXUS Mesh.", 
                "receipt_id": receipt_id,
                "mesh_trace_id": trace_id,
                "mesh_receipt": settle_data.get("receipt")
            }

    except Exception as e:
        payment_record.status = "failed"
        db.commit()
        return {"status": "failed", "message": f"NEXUS Mesh Connection Error: {str(e)}"}

