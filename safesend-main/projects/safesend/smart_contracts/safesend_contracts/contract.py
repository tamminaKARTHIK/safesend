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
        """Create the contract with default guardian and safe limit."""
        # Set a default guardian placeholder
        # CHANGE: Updated placeholder to emphasize user should replace it
        return Seq(
            self.guardian.set(Bytes("REPLACE_WITH_GUARDIAN_ADDRESS")),
            self.safe_limit.set(Int(0)),
        )

    # Set Guardian (only creator can set)
    @Application.external(authorize=Authorize.only_creator())
    def set_guardian(self, guardian: abi.Address, *, output: abi.String):
        """Set the guardian account for large transactions."""
        # CHANGE: added debug print to track guardian updates
        print("Debug: set_guardian called with address:", guardian.get())
        return Seq(
            self.guardian.set(guardian.get()),
            output.set("Guardian set successfully"),
        )

    # Set Safe Limit (only creator can set)
    @Application.external(authorize=Authorize.only_creator())
    def set_limit(self, limit: abi.Uint64, *, output: abi.String):
        """Set the maximum amount allowed for auto-approved transactions."""
        # CHANGE: added debug print to track safe limit updates
        print("Debug: set_limit called with amount:", limit.get())
        return Seq(
            self.safe_limit.set(limit.get()),
            output.set("Safe limit set successfully"),
        )

    # Helper function to check if transaction is safe
    def is_safe(self, amount: abi.Uint64):
        # CHANGE: added docstring for helper
        """Check if transaction amount is within the safe limit."""
        return amount.get() <= self.safe_limit.get()

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
        """Handle a transaction request."""
        # TODO: improve error handling here (e.g., check sender balance)
        # Debug log for tracking
        print("Debug LOG: request_transaction called by", sender.get(), "for amount:", amount.get())

        # CHANGE: added output message clarity
        return Seq(
            If(self.is_safe(amount))
            .Then(output.set(Concat(Bytes("Transaction auto-approved: "), Itob(amount.get()))))
            .Else(output.set(Concat(Bytes("Transaction pending guardian approval for amount: "), Itob(amount.get()))))
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
        """Approve transaction as the guardian."""
        # TODO: improve error handling here (e.g., ensure guardian exists)
        # Debug log for tracking
        print("Debug LOG: approve_transaction called by sender:", Txn.sender())

        # CHANGE: added helper for guardian existence check
        return Seq(
            Assert(self.guardian.get() != Bytes("")),
            Assert(Txn.sender() == self.guardian.get()),
            output.set(Concat(Bytes("Transaction approved by guardian for amount: "), Itob(amount.get())))
        )


# Boilerplate to allow CLI interaction
if __name__ == "__main__":
    app = SafeSendApp()
    spec = app.build()
    spec.export("artifacts")
