# This file doesn't have an equivalent file in the dss. This file
# just contains a list of common functions and data structures
# that solidity usually has as an automatic feature of the language,
# whereas python does not.
# Authored Colby Anderson

import time

from typing import Dict


# Represents a ticker for an asset, i.e. "ETH"
# or "USD", etc.
# [dss] Replicates bytes32 (for the most part)
class Ticker:
    def __init__(self, tick: str):
        self.tick = tick


# Represents the caller of a function, which
# could be simulated by a person with an account
# on the blockchain or a contract that exists on the
# blockchain
# [dss] Replicates address
class User:
    def __init__(self, name: str):
        self.name = name


# Raises an exception if the necessary condition is false.
# This loosely replaces the inbuilt "require" function from
# solidity.
# [solidity] Replicates require
def require(necessary_condition: bool, error_message: str):
    if not necessary_condition:
        raise Exception(error_message)


# Gets the current time (in seconds from Unix epoch).
# [solidity] Replicates block.timestamp
def get_current_blocktime() -> float:
    return time.time()


#
class Collateral:
    def __init__(self, sender: User, total_supply: float,
                 name: User, collateral_type: Ticker,
                 balance_of: Dict[User, float],
                 allowance: Dict[User, Dict[User, float]],
                 authorized_users: Dict[User, bool]):
        # A dictionary from users to bool, wherein [user] = True
        # if the user has authorization to access special methods
        # [dai.sol] Replicates wards
        self.authorized_users = authorized_users
        self.authorized_users[sender] = True
        # This represents the name of the class. When an object of this
        # class calls other functions in different classes, and these external
        # functions need the name of a caller, this name will be passed.
        self.name = name
        # The ticker of the collateral
        self.collateral_type = collateral_type
        # The total amount of the collateral in circulation (that has been minted, but not
        # burned).
        self.total_supply = total_supply
        # A dictionary that maps each User to how much of the collateral they have
        self.balance_of = balance_of
        # A dictionary that shows how much certain Users are allowed
        # to transfer (spend) for other Users.
        # User who owns the collateral -> User wanting to spend their collateral -> approved
        # amount to spend
        self.allowance = allowance

    # -------------------------------------------------------
    # -------------- Transferring Collateral ----------------
    # -------------------------------------------------------

    # This is a wrapper function around transfer_from. It will transfer
    # some amount of funds from the sender [caller of this function] to the receiver.
    # Returns True if the transfer was successful, False otherwise
    def transfer(self, sender: User, receiver: User, amount: float) -> bool:
        return self.transfer_from(sender=sender, source_account=sender,
                                  destination_account=receiver, amount=amount)

    # Transfers funds from the source account to the destination account if
    # the source account has enough funds to transfer, AND the source account is the
    # sender or has approved more than this amount of funds for the sender.
    # Returns True if the transfer was successful, False otherwise
    def transfer_from(self, sender: User, source_account: User,
                      destination_account: User, amount: float) -> bool:
        require(necessary_condition=self.balance_of.get(source_account, 0) >= amount,
                error_message="Affected user doesn't have enough collateral to burn")
        if source_account != sender:
            require(necessary_condition=self.allowance.get(source_account, False) is not False,
                    error_message="Affected user hasn't approved anyone to spend for him")
            require(necessary_condition=self.allowance[source_account].get(sender, 0) >= amount,
                    error_message="Affected user hasn't approved enough transferrable funds for the sender")
            self.allowance[source_account][sender] -= amount
        self.balance_of[source_account] -= amount
        self.balance_of[destination_account] += amount
        return True

    # -------------------------------------------------------
    # ----------- Creating/Destroying Collateral ------------
    # -------------------------------------------------------

    # Mints collateral (creates collateral and gives it to) for some beneficiary
    # if the sender [caller of the function] has authorization access.
    def mint(self, sender: User, beneficiary: User, amount: float):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.balance_of[beneficiary] += amount
        self.total_supply += amount

    # The sender will burn some amount of DAI for the affected user if
    # the affected user has enough funds to burn, AND the affected user is the
    # sender or has approved more than this amount of funds for the sender.
    def burn(self, sender: User, affected_user: User, amount: float):
        require(necessary_condition=self.balance_of.get(affected_user, 0) >= amount,
                error_message="Affected user doesn't have enough collateral to burn")
        if sender != affected_user:
            require(necessary_condition=self.allowance.get(affected_user, False) is not False,
                    error_message="Affected user hasn't approved anyone to spend for him")
            require(necessary_condition=self.allowance[affected_user].get(sender, 0) >= amount,
                    error_message="Affected user hasn't approved enough transferrable funds for the sender")
            self.allowance[affected_user][sender] -= amount
        self.balance_of[affected_user] -= amount
        self.total_supply -= amount

    # -------------------------------------------------------
    # ------ Approving Others For Fund Transfers ------------
    # -------------------------------------------------------

    # The sender [caller of the function] is approving some user to transfer
    # a certain amount of the sender's funds as if they were the sender.
    # Returns True if the function ran successfully, and False otherwise.
    def approve(self, sender: User, user: User, amount: float) -> bool:
        if self.allowance.get(sender, False) is False:
            self.allowance[sender] = {}
        self.allowance[sender][user] = amount
        return True

    # -------------------------------------------------------
    # ---------- Granting/Removing Authorization ------------
    # -------------------------------------------------------

    # Grants authorization for a specific user if the sender [caller
    # of the function] has authorization access.
    # [join.sol] Replicates rely(address guy) external auth
    def grant_authorization(self, sender: User, new_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.authorized_users[new_user] = True

    # Removes authorization for a specific user if the sender [caller
    # of the function] has authorization access.
    # [join.sol] Replicates deny(address guy) external auth
    def remove_authorization(self, sender: User, old_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.authorized_users[old_user] = False


# class SignedMessage:
#     def __init__(self):
#         pass
#
#
# class Signature:
#     def __init__(self):
#         pass
#
#
# def ec_recover():
#     pass
#
#
# def compute_message():
#     pass
