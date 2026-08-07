from dotenv import load_dotenv
load_dotenv()  # Load nexus-mesh/.env so ALGORAND_FACILITATOR_MNEMONIC is available

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

from app.registry.engine import engine
from app.settlement.adapters.algorand import (
    AlgorandGoPlausibleFacilitator,
    AlgorandSimulatorFacilitator
)
from app.settlement.adapters.ethereum import EVMSimulatorFacilitator
from app.settlement.adapters.solana import SVMSimulatorFacilitator

# Register Facilitators (Ordered by priority)
engine.register(AlgorandGoPlausibleFacilitator(), priority=1)
engine.register(AlgorandSimulatorFacilitator(), priority=2)
engine.register(EVMSimulatorFacilitator(), priority=1)
engine.register(SVMSimulatorFacilitator(), priority=1)

app = FastAPI(
    title="NEXUS x402 Settlement Mesh",
    version="1.0.0",
    description="Enterprise Multi-Chain Verification & Settlement Mesh for x402"
)

# Enable CORS for Resource Server communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)


