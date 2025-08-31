from beaker import sandbox, client
 from safesend_contracts.contract import SafeSendApp

# Get accounts from sandbox
accts = sandbox.get_accounts()
acct = accts[0]

# Initialize contract and client
app = SafeSendApp()
app_client = client.ApplicationClient(
    client=sandbox.get_algod_client(),
    app=app,
    signer=acct.signer,
)

# Set a new whitelisted address (e.g., second account)
new_whitelist = accts[1].address

# Call the contract's method
print(f"Updating whitelist to: {new_whitelist}")
result = app_client.call(
    method=app.update_whitelist,
    args=[new_whitelist],
)
print("✅ Whitelist updated successfully!")
print("Transaction ID:", result.tx_id)
