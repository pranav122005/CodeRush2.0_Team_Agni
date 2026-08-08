import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ALGORAND_NETWORK: str = os.getenv("ALGORAND_NETWORK", "testnet")
    ALGORAND_FACILITATOR_MNEMONIC: str = os.getenv("ALGORAND_FACILITATOR_MNEMONIC", "")
    ALGORAND_WALLET_ADDRESS: str = os.getenv("ALGORAND_WALLET_ADDRESS", "")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    # Required for every /api/v1/admin endpoint. Keep this server-side only.
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "")

    # PostgreSQL connection
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "nexus_x402")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

    # Ethereum / Sepolia
    ETH_RPC_URL: str = os.getenv("ETH_RPC_URL", "https://rpc.sepolia.org")
    ETH_WALLET_ADDRESS: str = os.getenv("ETH_WALLET_ADDRESS", "0x71C7656EC7ab88b098defB751B7401B5f6d8976F")

settings = Settings()
