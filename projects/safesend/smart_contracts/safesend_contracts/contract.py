from beaker import Application, ApplicationStateValue
from pyteal import abi, Txn, Global, Int, Assert, Seq, InnerTxnBuilder, TxnField, TxnType


# Define the application state
class SafeSendState:
    owner = ApplicationStateValue(stack_type=abi.Address, descr="Owner of the SafeSend contract")
    whitelisted_receiver = ApplicationStateValue(stack_type=abi.Address, descr="Allowed address to receive funds")
    pending_receiver = ApplicationStateValue(stack_type=abi.Address, descr="Receiver of the pending transaction")
    pending_amount = ApplicationStateValue(stack_type=abi.Uint64, descr="Amount of the pending transaction")
    transaction_pending = ApplicationStateValue(stack_type=abi.Bool, descr="Flag to indicate if a transaction is pending")


# Define the application
class SafeSendApp(Application):
    def __init__(self):
        super().__init__("SafeSend", state=SafeSendState())

    @Application.create
    def create_app(self, owner: abi.Address):
        return Seq(
            self.state.owner.set(owner),
            self.state.whitelisted_receiver.set(owner)
        )

    @Application.external
    def get_owner(self, *, output: abi.Address):
        return output.set(self.state.owner)

    @Application.external
    def get_whitelist(self, *, output: abi.Address):
        return output.set(self.state.whitelisted_receiver)

    def _update_whitelist_impl(self, new_receiver: abi.Address):
        return Seq(
            Assert(new_receiver.get() != Global.zero_address(), comment="Receiver cannot be zero address"),
            self.state.whitelisted_receiver.set(new_receiver)
        )

    @Application.external
    def update_whitelist(self, new_receiver: abi.Address):
        return self._update_whitelist_impl(new_receiver)

    @Application.external
    def initiate_transfer(self, receiver: abi.Address, amount: abi.Uint64):
        """Initiates a transfer by setting the pending transaction details."""
        return Seq(
            self.state.pending_receiver.set(receiver),
            self.state.pending_amount.set(amount),
            self.state.transaction_pending.set(Int(1))
        )

    @Application.external
    def confirm_transfer(self):
        """Confirms and executes a pending transaction."""
        return Seq(
            Assert(Txn.sender() == self.state.owner, comment="Only owner can confirm"),
            Assert(self.state.transaction_pending, comment="No pending transaction"),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: self.state.pending_receiver.get(),
                TxnField.amount: self.state.pending_amount.get(),
            }),
            InnerTxnBuilder.Submit(),
            self.state.pending_receiver.set(Global.zero_address()),
            self.state.pending_amount.set(Int(0)),
            self.state.transaction_pending.set(Int(0))
        )

    @Application.external
    def cancel_transfer(self):
        """Cancels a pending transaction."""
        return Seq(
            Assert(Txn.sender() == self.state.owner, comment="Only owner can cancel"),
            Assert(self.state.transaction_pending, comment="No pending transaction"),
            self.state.pending_receiver.set(Global.zero_address()),
            self.state.pending_amount.set(Int(0)),
            self.state.transaction_pending.set(Int(0))
        )

    @Application.external
    def execute_transfer(self, receiver: abi.Address, amount: abi.Uint64, *, output: abi.String):
        MAX_AMOUNT = Int(1_000_000)  # 1 Algo
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