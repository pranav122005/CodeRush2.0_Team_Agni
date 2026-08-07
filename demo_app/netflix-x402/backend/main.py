from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from schemas import X402PaymentPayload, PaymentResponse
from services.payment import process_payment
from fastapi.responses import FileResponse
from config import settings
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Netflix x402 Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/payments/verify", response_model=PaymentResponse)
def verify_payment(payload: X402PaymentPayload, db: Session = Depends(get_db)):
    """ Endpoint to process and settle the x402 payment """
    result = process_payment(payload, db)
    if result["status"] == "failed":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/api/v1/content/{content_id}")
def get_content(content_id: str, receipt_id: str = None, db: Session = Depends(get_db)):
    from models import Receipt, PaymentRecord
    if not receipt_id:
        raise HTTPException(
            status_code=402, 
            detail={
                "message": "Payment Required",
                "x402_payload_template": {
                    "amount": 1.50,
                    "currency": "USDC",
                    "asset_id": "10458941",
                    "resource_identifier": content_id,
                    "recipient_address": settings.ALGORAND_WALLET_ADDRESS
                }
            }
        )
        
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=403, detail="Invalid receipt")
        
    payment = db.query(PaymentRecord).filter(PaymentRecord.payment_id == receipt.payment_id).first()
    if not payment or payment.resource_identifier != content_id:
        raise HTTPException(status_code=403, detail="Receipt does not match this content")
        
    # Return mock video URL 
    return {"status": "success", "content_url": f"https://www.w3schools.com/html/mov_bbb.mp4"}

@app.get("/api/v1/receipts/{receipt_id}")
def get_receipt_pdf(receipt_id: str):
    filepath = os.path.join(os.path.dirname(__file__), "receipts", f"{receipt_id}.pdf")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Receipt not found")
    return FileResponse(filepath, media_type="application/pdf", filename=f"{receipt_id}.pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
