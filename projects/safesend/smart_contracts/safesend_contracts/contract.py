from beaker import Application, ApplicationStateValue
from pyteal import abi, Txn, Global, Int, Assert, Seq, InnerTxnBuilder, TxnField, TxnType

class SafeSendState:
    owner = ApplicationStateValue(stack_type=abi.Address, descr="Owner of the SafeSend contract")
    whitelisted_receiver = ApplicationStateValue(stack_type=abi.Address, descr="Allowed address to receive funds")

# ✅ Wrap the app in a class
class SafeSendApp(Application):
    def __init__(self):
        super().__init__("SafeSend", state=SafeSendState())

  @app.create
def create_app(owner: abi.Address):
    return Seq(
        app.state.owner.set(owner),
        app.state.whitelisted_receiver.set(owner)
    )

@app.external
def get_owner(*, output: abi.Address):
    return output.set(app.state.owner)

@app.external
def get_whitelist(*, output: abi.Address): 
    return output.set(app.state.whitelisted_receiver)


    def _update_whitelist_impl(self, new_receiver: abi.Address):
        return self.state.whitelisted_receiver.set(new_receiver)

    @Application.external
    def safe_transfer(self, receiver: abi.Address, amount: abi.Uint64, *, output: abi.String):
        MAX_AMOUNT = Int(1_000_000)
        return Seq(
            Assert(amount.get() <= MAX_AMOUNT, comment="Amount exceeds limit"),
            Assert(receiver.get() == self.state.whitelisted_receiver, comment="Receiver not allowed"),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: receiver.get(),
                TxnField.amount: amount.get(),
            }),
            InnerTxnBuilder.Submit(),
            output.set("Transfer successful"),
        )

    # Reusable decorator logic
    def authorize_only_owner(self, method):
        return method.authorize(lambda: Txn.sender() == self.state.owner)
