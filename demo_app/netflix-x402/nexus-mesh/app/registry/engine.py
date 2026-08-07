import time
from typing import List, Dict, Any
from app.registry.base import BaseFacilitator
from app.registry.circuit_breaker import CircuitBreaker

class FacilitatorEntry:
    def __init__(self, facilitator: BaseFacilitator, priority: int = 1):
        self.facilitator = facilitator
        self.priority = priority
        self.breaker = CircuitBreaker()
        self.last_latency_ms = 0.0

class FacilitatorEngine:
    def __init__(self):
        self._pool: List[FacilitatorEntry] = []

    def register(self, facilitator: BaseFacilitator, priority: int = 1):
        self._pool.append(FacilitatorEntry(facilitator, priority))

    def select(self, network: str) -> BaseFacilitator:
        candidates = [e for e in self._pool if e.facilitator.network == network]
        
        # 1. Try healthy live facilitators
        for entry in sorted(candidates, key=lambda x: x.priority):
            if not entry.facilitator.is_simulator and entry.breaker.can_execute():
                return entry.facilitator

        # 2. Fall back to Simulator facilitators
        for entry in candidates:
            if entry.facilitator.is_simulator:
                return entry.facilitator

        raise RuntimeError(f"No health-verified facilitator available for network: {network}")

    async def execute_settlement(self, network: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes settlement with automatic retry & failover across registered nodes."""
        candidates = sorted([e for e in self._pool if e.facilitator.network == network], key=lambda x: x.priority)
        
        for entry in candidates:
            if not entry.breaker.can_execute():
                continue

            start_time = time.time()
            try:
                result = await entry.facilitator.settle(payload)
                latency = (time.time() - start_time) * 1000
                entry.breaker.record_success()
                entry.last_latency_ms = latency
                
                # Attach note if this was a simulator fallback
                if entry.facilitator.is_simulator and len([e for e in candidates if not e.facilitator.is_simulator]) > 0:
                     result["note"] = f"Settled via fallback simulator ({entry.facilitator.name})"

                return result
            except Exception as e:
                entry.breaker.record_failure()
                print(f"Facilitator {entry.facilitator.name} failed: {e}. Trying failover...")

        raise RuntimeError(f"All facilitators for network {network} failed settlement.")

    def get_status(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": e.facilitator.name,
                "network": e.facilitator.network,
                "state": e.breaker.state.value,
                "is_simulator": e.facilitator.is_simulator,
                "failure_count": e.breaker.failure_count,
                "last_latency_ms": round(e.last_latency_ms, 2)
            }
            for e in self._pool
        ]

engine = FacilitatorEngine()
