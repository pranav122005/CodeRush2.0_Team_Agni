from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class PaymentRecord(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String, unique=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    currency = Column(String)
    resource_identifier = Column(String)
    status = Column(String) # 'pending', 'succeeded', 'failed'
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Receipt(Base):
    __tablename__ = "receipts"
    
    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(String, unique=True, index=True)
    payment_id = Column(String, index=True)
    file_path = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
