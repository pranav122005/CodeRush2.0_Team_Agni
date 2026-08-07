import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "NEXUS x402 Settlement Mesh"
    VERSION: str = "1.0.0"
    SECRET_KEY: bytes = os.getenv("NEXUS_HMAC_SECRET", "NEXUS_HMAC_SECRET_KEY_2026_DEFAULT").encode('utf-8')
    PRIMARY_ALGORAND_FACILITATOR: str = os.getenv("FACILITATOR_URL", "https://facilitator.goplausible.xyz")
    ALGORAND_ALGOD_SERVER: str = os.getenv("ALGOD_SERVER", "https://testnet-api.algonode.cloud")
    ALGORAND_USDC_ASA_ID: int = int(os.getenv("USDC_ASA_ID", "10458941"))
    PORT: int = int(os.getenv("PORT", "8001"))

settings = Settings()
