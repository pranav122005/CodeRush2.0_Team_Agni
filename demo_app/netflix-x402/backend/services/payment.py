from sqlalchemy.orm import Session
from models import PaymentRecord, Receipt
from schemas import X402PaymentPayload
from services.algorand import verify_and_submit_transaction
from services.llm_registry import check_duplicate_transaction
from services.receipt import generate_pdf_receipt

def process_payment(payload: X402PaymentPayload, db: Session):
    # 1. Idempotency Check (Local DB)
    existing = db.query(PaymentRecord).filter(PaymentRecord.payment_id == payload.payment_id).first()
    if existing:
        return {"status": "failed", "message": "Duplicate payment_id detected."}
        
    existing_tx = db.query(PaymentRecord).filter(PaymentRecord.transaction_id == payload.transaction_id).first()
    if existing_tx:
         return {"status": "failed", "message": "Duplicate transaction_id detected."}

    # 2. LLM Registry Check
    is_safe = check_duplicate_transaction(payload.payment_id, payload.transaction_id)
    if not is_safe:
        return {"status": "failed", "message": "LLM Registry rejected this transaction."}

    # 3. Save pending state
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
    
    # 4. Submit to Algorand
    algo_result = verify_and_submit_transaction(payload.signature)
    
    if algo_result["status"] == "success":
        payment_record.status = "succeeded"
        db.commit()
        
        # 5. Generate Receipt
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
        
        return {"status": "success", "message": "Payment settled successfully.", "receipt_id": receipt_id}
    else:
        payment_record.status = "failed"
        db.commit()
        return {"status": "failed", "message": algo_result.get("error", "Network failure")}
