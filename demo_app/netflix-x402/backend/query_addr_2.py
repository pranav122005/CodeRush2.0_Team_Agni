from algosdk.v2client import algod

client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
addr = "7YEYTXHWKQMFZRU55TSNGBFAQNGF3U2VJZ2QEGQZNC2TTUUIA2YY6MUB3E"

try:
    account_info = client.account_info(addr)
    algo_balance = account_info.get("amount", 0) / 1_000_000
    print(f"Address: {addr}")
    print(f"ALGO Balance: {algo_balance:.6f} ALGO")
except Exception as e:
    print(f"Error querying address: {e}")
