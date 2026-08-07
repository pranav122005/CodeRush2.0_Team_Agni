import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "CLOSED"      # Healthy
    OPEN = "OPEN"          # Failing, bypass facilitator
    HALF_OPEN = "HALF_OPEN"# Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 20.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            return False
        return True

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
