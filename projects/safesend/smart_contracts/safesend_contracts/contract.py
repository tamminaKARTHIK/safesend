from beaker import sandbox, client
from import SafeSendApp

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

from beaker import Application, ApplicationStateValue
from pyteal import abi, Txn, Global, If, Assert, Expr, InnerTxnBuilder, InnerTxn, TxnType

class SafeSendState:
    owner = ApplicationStateValue(stack_type=abi.Address, descr="Owner of the SafeSend contract")

app = Application("SafeSend", state=SafeSendState())

@app.create
def create_app(owner: abi.Address):
    return app.state.owner.set(owner)

@app.external
def get_owner(*, output: abi.Address):
    return output.set(app.state.owner)

@app.external
def safe_transfer(
    receiver: abi.Address,
    amount: abi.Uint64,
    *,
    output: abi.String
):
    MAX_AMOUNT = Int(1_000_000)  # 1 Algo = 1,000,000 microAlgos

    # Replace this with actual whitelisting logic later
    whitelist_address = Global.creator_address()

    # Validate receiver and amount
    return Seq(
        Assert(amount.get() <= MAX_AMOUNT, comment="Amount exceeds allowed limit"),
        Assert(receiver.get() == whitelist_address, comment="Receiver not whitelisted"),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: receiver.get(),
            TxnField.amount: amount.get(),
        }),
        InnerTxnBuilder.Submit(),
        output.set("Transfer successful"),
    )
