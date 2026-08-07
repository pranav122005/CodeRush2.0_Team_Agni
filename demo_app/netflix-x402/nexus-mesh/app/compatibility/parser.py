import base64
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class PaymentRequirement(BaseModel):
    scheme: str = "exact"
    price: str
    network: str
    payTo: str
    asset_id: Optional[str] = None

class x402Payload(BaseModel):
    x402_version: int = Field(default=2, alias="x402Version")
    scheme: str = "exact"
    network: str
    payload: Dict[str, Any]
    resource_url: Optional[str] = None
    nonce: Optional[str] = None

class PayloadParser:
    @staticmethod
    def parse_header(header_str: str) -> x402Payload:
        """Parses Base64 encoded or raw JSON Payment-Signature headers."""
        try:
            if header_str.startswith("{"):
                raw_json = header_str
            else:
                raw_json = base64.b64decode(header_str).decode("utf-8")
            
            data = json.loads(raw_json)
            
            # Extract nested fields if standard v2 structure
            scheme = data.get("scheme", "exact")
            network = data.get("network", "algorand:testnet")
            payload_data = data.get("payload", data)
            
            return x402Payload(
                x402Version=data.get("x402Version", 2),
                scheme=scheme,
                network=network,
                payload=payload_data,
                resource_url=data.get("resource", {}).get("url") if isinstance(data.get("resource"), dict) else data.get("resource_url"),
                nonce=data.get("nonce")
            )
        except Exception as e:
            raise ValueError(f"Failed to parse x402 payment header: {str(e)}")
