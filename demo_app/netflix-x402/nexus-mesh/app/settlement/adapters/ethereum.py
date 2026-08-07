import uuid
import asyncio
from typing import Dict, Any
from app.registry.base import BaseFacilitator

class EVMSimulatorFacilitator(BaseFacilitator):
    def __init__(self):
        super().__init__(name="Ethereum EVM Simulator", network="ethereum:sepolia", is_simulator=True)

    async def verify(self, payload: Dict[str, Any], requirement: Dict[str, Any]) -> bool:
        return True

    async def settle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        tx_hash = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:32]}"
        return {
            "settled": True,
            "txnHash": tx_hash,
            "blockNumber": 5892104,
            "simulator": True
        }

    async def check_health(self) -> bool:
        return True
