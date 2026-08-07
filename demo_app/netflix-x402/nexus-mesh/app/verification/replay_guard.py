import hashlib
import json
import time
from typing import Dict, Tuple, Optional

class ReplayGuard:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        # Maps payload_hash -> (timestamp, status, trace_id)
        self._cache: Dict[str, Tuple[float, str, str]] = {}

    def compute_hash(self, payload_dict: dict) -> str:
        """Computes a deterministic SHA-256 fingerprint for transaction payloads."""
        serialized = json.dumps(payload_dict, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def is_duplicate(self, payload_hash: str) -> Tuple[bool, Optional[str]]:
        """Returns (is_duplicate, existing_trace_id)."""
        self._cleanup()
        if payload_hash in self._cache:
            _, status, trace_id = self._cache[payload_hash]
            return True, trace_id
        return False, None

    def register(self, payload_hash: str, trace_id: str, status: str = "REGISTERED"):
        self._cache[payload_hash] = (time.time(), status, trace_id)

    def update_status(self, payload_hash: str, new_status: str):
        if payload_hash in self._cache:
            ts, _, trace_id = self._cache[payload_hash]
            self._cache[payload_hash] = (ts, new_status, trace_id)

    def _cleanup(self):
        now = time.time()
        expired = [h for h, (ts, _, _) in self._cache.items() if now - ts > self.ttl_seconds]
        for h in expired:
            del self._cache[h]

replay_guard = ReplayGuard()
