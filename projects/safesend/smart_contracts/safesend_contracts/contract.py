from beaker import Application, ApplicationStateValue
from pyteal import abi, Txn, Global, Int, Assert, Seq, InnerTxnBuilder, TxnField, TxnType

class SafeSendState:
    owner = ApplicationStateValue(stack_type=abi.Address, descr="Owner of the SafeSend contract")
    whitelisted_receiver = ApplicationStateValue(stack_type=abi.Address, descr="Allowed address to receive funds")

app = Application("SafeSend", state=SafeSendState())

@app.create
def create_app(owner: abi.Address):
    return Seq(
        app.state.owner.set(owner),
        app.state.whitelisted_receiver.set(owner)  # default to owner
    )

@app.external
def get_owner(*, output: abi.Address):
    return output.set(app.state.owner)

@app.external
def update_whitelist(new_receiver: abi.Address):
    return Seq(
        Assert(Txn.sender() == app.state.owner, comment="Only owner can update whitelist"),
        app.state.whitelisted_receiver.set(new_receiver)
    )

@app.external
def safe_transfer(
    receiver: abi.Address,
    amount: abi.Uint64,
    *,
    output: abi.String
):
    MAX_AMOUNT = Int(1_000_000)  # 1 Algo

    return Seq(
        Assert(amount.get() <= MAX_AMOUNT, comment="Amount exceeds limit"),
        Assert(receiver.get() == app.state.whitelisted_receiver, comment="Receiver not allowed"),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: receiver.get(),
            TxnField.amount: amount.get(),
        }),
        InnerTxnBuilder.Submit(),
        output.set("Transfer successful"),
    )
# Decorator to restrict access to the owner only
def only_owner(method):
    return method.authorize(
        lambda: Txn.sender() == app.state.owner
    )
