import uuid
import time
import httpx
from enum import Enum
from typing import Dict, Any, Optional

class SettlementState(Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    SETTLING = "SETTLING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"

class SettlementService:
    def __init__(self):
        # Maps trace_id -> record
        self._records: Dict[str, Dict[str, Any]] = {}

    def create_trace(self, network: str, amount: str, pay_to: str) -> str:
        trace_id = f"trc_{uuid.uuid4().hex[:16]}"
        self._records[trace_id] = {
            "trace_id": trace_id,
            "payment_id": f"pay_{uuid.uuid4().hex[:12]}",
            "network": network,
            "amount": amount,
            "pay_to": pay_to,
            "state": SettlementState.PENDING.value,
            "tx_hash": None,
            "error": None,
            "created_at": time.time(),
            "timeline": [{"event": "TRACE_CREATED", "timestamp": time.time()}]
        }
        return trace_id

    def update_state(self, trace_id: str, state: SettlementState, tx_hash: Optional[str] = None, error: Optional[str] = None):
        if trace_id in self._records:
            record = self._records[trace_id]
            record["state"] = state.value
            if tx_hash:
                record["tx_hash"] = tx_hash
            if error:
                record["error"] = error
            record["timeline"].append({"event": f"STATE_CHANGED_TO_{state.value}", "timestamp": time.time()})

    def get_record(self, trace_id: str) -> Optional[Dict[str, Any]]:
        return self._records.get(trace_id)

settlement_service = SettlementService()
