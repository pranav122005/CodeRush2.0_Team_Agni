import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ALGORAND_NETWORK: str = os.getenv("ALGORAND_NETWORK", "testnet")
    ALGORAND_FACILITATOR_MNEMONIC: str = os.getenv("ALGORAND_FACILITATOR_MNEMONIC", "")
    ALGORAND_WALLET_ADDRESS: str = os.getenv("ALGORAND_WALLET_ADDRESS", "")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # PostgreSQL connection
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "nexus_x402")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

settings = Settings()
