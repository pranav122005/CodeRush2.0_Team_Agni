from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseFacilitator(ABC):
    def __init__(self, name: str, network: str, is_simulator: bool = False):
        self.name = name
        self.network = network          # e.g., "algorand:testnet", "ethereum:sepolia"
        self.is_simulator = is_simulator

    @abstractmethod
    async def verify(self, payload: Dict[str, Any], requirement: Dict[str, Any]) -> bool:
        """Verifies if the signed payload matches requirements without submitting."""
        pass

    @abstractmethod
    async def settle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submits transaction to the network and returns settlement proof."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Checks if this facilitator endpoint is responsive."""
        pass
