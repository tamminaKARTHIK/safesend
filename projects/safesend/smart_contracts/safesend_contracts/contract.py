from beaker import sandbox, client
from contracts.safesend import SafeSendApp

# Initialize app
app = SafeSendApp()

# Use sandbox for deployment
accts = sandbox.get_accounts()
acct = accts[0]

app_client = client.ApplicationClient(
    client=sandbox.get_algod_client(),
    app=app,
    signer=acct.signer,
)

# Deploy the contract
app_id, app_addr, txid = app_client.create()
print(f"Deployed SafeSend app ID: {app_id}")
print(f"App Address: {app_addr}")
