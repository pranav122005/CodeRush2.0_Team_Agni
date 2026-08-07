from algosdk.v2client import algod

client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
addr = "XFS5PAPJZO35Z4AYCZLRQMIKPPCGJUX5PIMWISTW5J22ILCX6ZQG7MGJHU"

try:
    account_info = client.account_info(addr)
    algo_balance = account_info.get("amount", 0) / 1_000_000
    print(f"Address: {addr}")
    print(f"ALGO Balance: {algo_balance:.6f} ALGO")
    
    assets = account_info.get("assets", [])
    print(f"\nAssets found in this account ({len(assets)}):")
    for asset in assets:
        asset_id = asset.get("asset-id")
        amount = asset.get("amount")
        try:
            asset_info = client.asset_info(asset_id)
            params = asset_info.get("params", {})
            name = params.get("name", "Unknown")
            unit = params.get("unit-name", "")
            decimals = params.get("decimals", 0)
            formatted_amount = amount / (10 ** decimals)
            print(f"  - Asset ID: {asset_id} | Name: {name} ({unit}) | Balance: {formatted_amount}")
        except Exception:
            print(f"  - Asset ID: {asset_id} | Raw Balance: {amount}")
except Exception as e:
    print(f"Error querying address: {e}")
