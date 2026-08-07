from fastapi import APIRouter, HTTPException, Header, Response, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.compatibility.parser import PayloadParser, PaymentRequirement
from app.verification.replay_guard import replay_guard
from app.registry.engine import engine
from app.settlement.state_machine import settlement_service, SettlementState
from app.receipt.generator import receipt_service

api_router = APIRouter(prefix="/api/v1")

class VerifyRequest(BaseModel):
    payment_header: str
    requirement: PaymentRequirement

class SettleRequest(BaseModel):
    trace_id: str
    payment_header: str

@api_router.post("/verify")
def verify_payment(req: VerifyRequest):
    try:
        parsed = PayloadParser.parse_header(req.payment_header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check Replay Guard
    payload_hash = replay_guard.compute_hash(parsed.payload)
    is_dup, existing_trace = replay_guard.is_duplicate(payload_hash)
    
    if is_dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate payment payload detected. Trace ID: {existing_trace}"
        )

    # Register Trace
    trace_id = settlement_service.create_trace(
        network=parsed.network,
        amount=req.requirement.price,
        pay_to=req.requirement.payTo
    )
    
    replay_guard.register(payload_hash, trace_id)
    settlement_service.update_state(trace_id, SettlementState.VERIFIED)

    return {
        "valid": True,
        "trace_id": trace_id,
        "network": parsed.network,
        "amount": req.requirement.price
    }

@api_router.post("/settle")
async def settle_payment(req: SettleRequest):
    record = settlement_service.get_record(req.trace_id)
    if not record:
        raise HTTPException(status_code=404, detail="Invalid trace_id")

    try:
        parsed = PayloadParser.parse_header(req.payment_header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # Enrich payload with settlement details from the trace record
        enriched_payload = {
            **parsed.payload,
            "amount":    record.get("amount", 1.5),
            "recipient": record.get("pay_to", ""),
        }
        settlement_res = await engine.execute_settlement(
            network=parsed.network,
            payload=enriched_payload
        )
        tx_hash = settlement_res.get("txnHash", f"tx_{req.trace_id}")
        settlement_service.update_state(req.trace_id, SettlementState.SETTLED, tx_hash=tx_hash)
    except Exception as e:
        settlement_service.update_state(req.trace_id, SettlementState.FAILED, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

    # Issue Receipt
    receipt = receipt_service.issue_receipt(
        payment_id=record["payment_id"],
        trace_id=req.trace_id,
        network=record["network"],
        tx_hash=tx_hash,
        amount=record["amount"],
        recipient=record["pay_to"]
    )

    response_data = {
        "settled": True,
        "trace_id": req.trace_id,
        "tx_hash": tx_hash,
        "receipt": receipt
    }
    
    if "note" in settlement_res:
         response_data["note"] = settlement_res["note"]

    return response_data

@api_router.get("/receipt/{receipt_id}")
def get_receipt(receipt_id: str):
    return {"status": "valid", "receipt_id": receipt_id}

@api_router.get("/trace/{trace_id}")
def get_trace(trace_id: str):
    record = settlement_service.get_record(trace_id)
    if not record:
        raise HTTPException(status_code=404, detail="Trace ID not found")
    return record

@api_router.get("/health")
def health_check():
    return {
        "status": "ok",
        "mesh": "NEXUS Settlement Mesh",
        "facilitators": engine.get_status()
    }

@api_router.get("/facilitators")
def list_facilitators():
    return {"facilitators": engine.get_status()}
