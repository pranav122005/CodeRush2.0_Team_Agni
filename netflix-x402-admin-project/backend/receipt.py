import os
import uuid
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

RECEIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "receipts")
os.makedirs(RECEIPTS_DIR, exist_ok=True)

def generate_pdf_receipt(payment_id: str, tx_id: str, amount: float, currency: str, resource_id: str) -> str:
    receipt_id = f"RCPT-{uuid.uuid4().hex[:8].upper()}"
    filename = f"{receipt_id}.pdf"
    filepath = os.path.join(RECEIPTS_DIR, filename)
    
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "x402 Payment Receipt")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 710, f"Receipt ID: {receipt_id}")
    c.drawString(100, 690, f"Date: {datetime.utcnow().isoformat()}Z")
    c.drawString(100, 670, f"Payment ID: {payment_id}")
    c.drawString(100, 650, f"Transaction ID: {tx_id}")
    c.drawString(100, 630, f"Amount: {amount} {currency}")
    c.drawString(100, 610, f"Resource: {resource_id}")
    c.drawString(100, 590, "Status: SETTLED")
    
    c.save()
    
    return receipt_id
