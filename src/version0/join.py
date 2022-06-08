# This file replicates the logic of join.sol of the makerdao/dss
# repository. join.sol can be found here: https://github.com/makerdao/dss/blob/master/src/join.sol
# Authored by Colby Anderson

from typing import Dict

from src.version0.bank_vat import Bank
from src.version0.dai import Dai
from src.version0.primitives import User, require, Ticker, Collateral


class GemJoin:
    def __init__(self, sender: User,
                 authorized_users: Dict[User, bool],
                 bank: Bank, collateral_type: Ticker,
                 collateral: Collateral, live: bool):
        # A dictionary from users to bool, wherein [user] = True
        # if the user has authorization to access special methods
        # [join.sol] Replicates wards
        self.authorized_users = authorized_users
        self.authorized_users[sender] = True
        # [join.sol] Replicates vat
        self.bank = bank
        # [join.sol] Replicates ilk
        self.collateral_type = collateral_type
        # [join.sol] Replicates gem
        self.collateral = collateral
        # [join.sol] Replicates live
        self.live = live
        # This represents the name of the class. When an object of this
        # class calls other functions in different classes, and these external
        # functions need the name of a caller, this name will be passed.
        self.name = User("GemJoin")

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

    # -------------------------------------------------------
    # ------------------------ Setters ----------------------
    # -------------------------------------------------------

    # [join.sol] Replicates cage
    def turn_off(self, sender: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.live = False

    # [join.sol] Replicates join
    def join(self, sender: User, loan_owner: User, amount: float):
        require(necessary_condition=self.live is True,
                error_message="GemJoin is turned off")
        self.collateral.transfer_from(sender, self.name, amount)
        self.bank.modify_collateral(collateral_type=self.collateral_type,
                                    user=loan_owner, delta_collateral_amount=amount)

    # [join.sol] Replicates exit
    def exit(self, sender: User, user: User, amount: float):
        self.collateral.transfer_from(self.name, user, amount)
        self.bank.modify_collateral(collateral_type=self.collateral_type,
                                    user=sender, delta_collateral_amount=amount * -1)


class DaiJoin:
    def __init__(self, sender: User,
                 authorized_users: Dict[User, bool],
                 bank: Bank,
                 dai: Dai, live: bool):
        # A dictionary from users to bool, wherein [user] = True
        # if the user has authorization to access special methods
        # [join.sol] Replicates wards
        self.authorized_users = authorized_users
        self.authorized_users[sender] = True
        # [join.sol] Replicates vat
        self.bank = bank
        # [join.sol] Replicates dai
        self.dai = dai
        # [join.sol] Replicates live
        self.live = live
        # This represents the name of the class. When an object of this
        # class calls other functions in different classes, and these external
        # functions need the name of a caller, this name will be passed.
        self.name = User("DaiJoin")

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

    # -------------------------------------------------------
    # ------------------------ Setters ----------------------
    # -------------------------------------------------------

    # [join.sol] Replicates cage
    def turn_off(self, sender: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.live = False

    # [join.sol] Replicates join
    def join(self, sender: User, user: User, amount: float):
        self.dai.burn(sender, amount)
        self.bank.transfer_debt(sender=self.name, user1=self.name,
                                user2=user, delta_debt_amount=amount)

    # [join.sol] Replicates exit
    def exit(self, sender: User, user: User, amount: float):
        require(necessary_condition=self.live is True,
                error_message="DaiJoin is turned off")
        self.dai.mint(user, amount)
        self.bank.transfer_debt(sender=self.name, user1=sender,
                                user2=self.name, delta_debt_amount=amount)
