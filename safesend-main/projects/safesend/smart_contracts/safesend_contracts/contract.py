from beaker import Application, GlobalStateValue, Authorize, client
from pyteal import *

# Define SafeSend Contract
class SafeSendApp(Application):

    # Guardian (address that approves large transactions)
    guardian = GlobalStateValue(
        stack_type=TealType.bytes, descr="Guardian account"
    )

    # Safe transaction limit (microAlgos)
    safe_limit = GlobalStateValue(
        stack_type=TealType.uint64, descr="Limit below which txns are auto-approved"
    )

    @Application.create
    def create(self):
        return Seq(
            self.guardian.set(Bytes("")),
            self.safe_limit.set(Int(0)),
        )

    # Set Guardian (only creator can set)
    @Application.external(authorize=Authorize.only_creator())
    def set_guardian(self, guardian: abi.Address, *, output: abi.String):
        return Seq(
            self.guardian.set(guardian.get()),
            output.set("Guardian set successfully"),
        )

    # Set Safe Limit (only creator can set)
    @Application.external(authorize=Authorize.only_creator())
    def set_limit(self, limit: abi.Uint64, *, output: abi.String):
        return Seq(
            self.safe_limit.set(limit.get()),
            output.set("Safe limit set successfully"),
        )

    # Request Transaction
    @Application.external
    def request_transaction(
        self,
        sender: abi.Address,
        receiver: abi.Address,
        amount: abi.Uint64,
        *,
        output: abi.String,
    ):
        # TODO: improve error handling here (e.g., check sender balance)
        # Debug log for tracking
        print("Debug: request_transaction called with sender:", sender.get(), "amount:", amount.get())
        return Seq(
            If(amount.get() <= self.safe_limit.get())
            .Then(output.set("Transaction auto-approved"))
            .Else(
                output.set("Transaction pending guardian approval")
            )
        )

    # Guardian Approves Transaction
    @Application.external
    def approve_transaction(
        self,
        sender: abi.Address,
        receiver: abi.Address,
        amount: abi.Uint64,
        *,
        output: abi.String,
    ):
        # TODO: improve error handling here (e.g., ensure guardian exists)
        # Debug log for tracking
        print("Debug: approve_transaction called by sender:", Txn.sender())
        return Seq(
            Assert(Txn.sender() == self.guardian.get()),
            output.set("Transaction approved by guardian"),
        )


# Boilerplate to allow CLI interaction
if __name__ == "__main__":
    app = SafeSendApp()
    spec = app.build()
    spec.export("artifacts")
