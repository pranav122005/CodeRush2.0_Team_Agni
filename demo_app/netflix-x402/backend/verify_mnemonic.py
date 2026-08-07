from algosdk import mnemonic, account
from algosdk.v2client import algod

phrase = "nasty jaguar action tray match name farm current blouse scan escape such nerve kind craft rice bullet canal pave busy when flight culture about verb"
target = "XFS5PAPJZO35Z4AYCZLRQMIKPPCGJUX5PIMWISTW5J22ILCX6ZQG7MGJHU"

try:
    pk = mnemonic.to_private_key(phrase)
    addr = account.address_from_private_key(pk)
    print(f"Recovered Address: {addr}")
    if addr == target:
        print("SUCCESS: Mnemonic matches the wallet address XFS5PAP...!")
    else:
        print(f"MISMATCH! Got: {addr}")
        print(f"Expected:      {target}")
except Exception as e:
    print(f"Error: {e}")

# Also query the real testnet balance
try:
    client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
    info = client.account_info(target)
    algo = info.get("amount", 0) / 1_000_000
    print(f"\nTestnet balance for {target[:20]}...")
    print(f"  ALGO: {algo:.6f}")
    for a in info.get("assets", []):
        if a["asset-id"] == 10458941:
            print(f"  USDC (Asset 10458941): {a['amount'] / 1_000_000:.2f}")
except Exception as e:
    print(f"Error querying testnet: {e}")
