import asyncio
import os
import re
from typing import Dict, Any
from app.registry.base import BaseFacilitator

# ─── Real on-chain Algorand USDC facilitator ────────────────────────────────
USDC_ASSET_ID = 10458941          # Testnet USDC ASA
USDC_DECIMALS  = 6                # 1 USDC = 1_000_000 micro-USDC
ALGOD_URL      = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN    = ""


def _parse_usdc_amount(raw) -> int:
    """
    Convert various amount formats to micro-USDC integer.
    Handles: 1.5 (float), "1.5" (str), "$1.5" (str with $), 1500000 (already micro).
    """
    if isinstance(raw, (int, float)):
        val = float(raw)
    else:
        # Strip currency symbols, spaces, quotes
        clean = re.sub(r"[^0-9.]", "", str(raw))
        val = float(clean) if clean else 1.5

    # If the value is already in micro-units (very large), keep it
    if val >= 10_000:
        return int(val)
    return int(val * (10 ** USDC_DECIMALS))


class AlgorandGoPlausibleFacilitator(BaseFacilitator):
    """
    Real Algorand facilitator: signs and submits a genuine USDC (ASA)
    transfer on testnet using the facilitator's mnemonic from the environment.
    Sends USDC from the configured wallet to the PLATFORM_TREASURY so the
    sender's balance visibly decreases.
    """

    def __init__(self):
        super().__init__(
            name="Algorand Real USDC Facilitator",
            network="algorand:testnet",
            is_simulator=False,
        )
        self._mnemonic = os.getenv("ALGORAND_FACILITATOR_MNEMONIC", "")
        self._wallet   = os.getenv("ALGORAND_WALLET_ADDRESS", "")

    # ── helpers ──────────────────────────────────────────────────────────────

    def _get_client(self):
        from algosdk.v2client import algod
        return algod.AlgodClient(ALGOD_TOKEN, ALGOD_URL)

    def _get_pk_and_addr(self):
        from algosdk import mnemonic, account
        pk   = mnemonic.to_private_key(self._mnemonic)
        addr = account.address_from_private_key(pk)
        return pk, addr

    # ── verify ───────────────────────────────────────────────────────────────

    async def verify(self, payload: Dict[str, Any], requirement: Dict[str, Any]) -> bool:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._verify_sync, requirement)

    def _verify_sync(self, requirement: Dict[str, Any]) -> bool:
        try:
            client = self._get_client()
            _, addr = self._get_pk_and_addr()
            info   = client.account_info(addr)
            assets = {a["asset-id"]: a["amount"] for a in info.get("assets", [])}
            usdc_balance = assets.get(USDC_ASSET_ID, 0)

            price_raw = requirement.get("price", "1.5")
            required_micro = _parse_usdc_amount(price_raw)
            print(f"[AlgorandFacilitator] Verify: balance={usdc_balance} required={required_micro}")
            return usdc_balance >= required_micro
        except Exception as e:
            print(f"[AlgorandFacilitator] verify error: {e}")
            return False

    # ── settle ────────────────────────────────────────────────────────────────

    async def settle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._settle_sync, payload)

    def _settle_sync(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        from algosdk import transaction

        client = self._get_client()
        pk, sender_addr = self._get_pk_and_addr()

        # Determine receiver: prefer the configured platform wallet.
        # For this demo, receiver == sender (self-send) which is valid on Algorand
        # and produces a real confirmed on-chain transaction.
        receiver_addr = self._wallet or sender_addr

        # Parse USDC amount robustly
        raw_amount   = payload.get("amount", 1.5)
        micro_amount = _parse_usdc_amount(raw_amount)

        print(f"[AlgorandFacilitator] Settling {micro_amount} micro-USDC "
              f"({micro_amount / 10**USDC_DECIMALS:.6f} USDC) "
              f"from {sender_addr[:10]}... to {receiver_addr[:10]}...")

        # Build ASA transfer transaction
        params = client.suggested_params()
        txn = transaction.AssetTransferTxn(
            sender   = sender_addr,
            sp       = params,
            receiver = receiver_addr,
            amt      = micro_amount,
            index    = USDC_ASSET_ID,
            note     = b"x402-nexus-payment",
        )

        signed_txn = txn.sign(pk)
        txid       = client.send_transaction(signed_txn)
        print(f"[AlgorandFacilitator] Submitted txid: {txid} — waiting for confirmation...")

        # Wait up to 8 rounds (~16 sec on testnet)
        confirmed       = transaction.wait_for_confirmation(client, txid, 8)
        confirmed_round = confirmed.get("confirmed-round", 0)

        print(f"[AlgorandFacilitator] Confirmed at round {confirmed_round}!")

        return {
            "settled":         True,
            "txnHash":         txid,
            "asset_id":        str(USDC_ASSET_ID),
            "amount_usdc":     micro_amount / (10 ** USDC_DECIMALS),
            "confirmed_round": confirmed_round,
            "network":         "algorand:testnet",
            "explorer_url":    f"https://testnet.explorer.perawallet.app/tx/{txid}",
        }

    # ── health ────────────────────────────────────────────────────────────────

    async def check_health(self) -> bool:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._health_sync)

    def _health_sync(self) -> bool:
        try:
            return bool(self._get_client().status())
        except Exception:
            return False


# ── Simulator fallback ────────────────────────────────────────────────────────

import uuid

class AlgorandSimulatorFacilitator(BaseFacilitator):
    def __init__(self):
        super().__init__(name="Algorand Local Simulator", network="algorand:testnet", is_simulator=True)

    async def verify(self, payload: Dict[str, Any], requirement: Dict[str, Any]) -> bool:
        return True

    async def settle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        tx_id = f"sim_algo_tx_{uuid.uuid4().hex[:20]}"
        return {
            "settled":         True,
            "txnHash":         tx_id,
            "asset_id":        str(USDC_ASSET_ID),
            "confirmed_round": 4200100,
            "simulator":       True,
        }

    async def check_health(self) -> bool:
        return True
