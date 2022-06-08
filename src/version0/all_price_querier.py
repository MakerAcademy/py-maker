# This file replicates the logic of spot.sol of the makerdao/dss
# repository. spot.sol can be found here: https://github.com/makerdao/dss/blob/master/src/spot.sol
# Authored by Colby Anderson

from typing import Dict

from src.version0.bank_vat import Bank
from src.version0.primitives import Ticker, User, require
from src.version0.single_price_querier import SingleCollateralPriceQuerier


# This represents information for a supported collateral type.
# Specifically, it stores where to query from, and the liquidation
# ratio which is used in the calculation of the spot price.
# [spot.sol] Replicates struct Ilk
class CollateralInfoForQuerying:
    def __init__(self, single_price_querier: SingleCollateralPriceQuerier,
                 liquidation_ratio: float):
        # [spot.sol] Replicates pip
        self.single_price_querier = single_price_querier
        # [spot.sol] Replicates mat
        self.liquidation_ratio = liquidation_ratio


# Responsible for interfacing between the Bank and all the different
# SingleCollateralPriceQuerier.
# [spot.sol] Replicates Spotter
class AllCollateralPriceQuerier:
    def __init__(self, sender: User, collateral_infos: Dict[Ticker, CollateralInfoForQuerying],
                 bank: Bank, querier_is_online: bool,
                 authorized_users: Dict[User, bool]):
        # [spot.sol] Replicates ilks
        self.collateral_infos = collateral_infos
        # [spot.sol] Replicates vat
        self.bank = bank
        # [spot.sol] Replicates live
        self.querier_is_online = querier_is_online
        # [spot.sol] Replicates wards
        self.authorized_users = authorized_users
        self.authorized_users[sender] = True
        # This represents the name of the class. When an object of this
        # class calls other functions in different classes, and these external
        # functions need the name of a caller, this name will be passed.
        self.name = User("AllCollateralPriceQuerier")

    # -------------------------------------------------------
    # ----------------- Updating Spot Price -----------------
    # -------------------------------------------------------

    # Pulls the spot price for a collateral type from the respective
    # SingleCollateralPriceQuerier and updates the Bank with the new
    # spot price.
    # [spot.sol] Replicates poke
    # TODO: Fix math in calculation of spot price
    def poke(self, collateral_type: Ticker):
        feed = self.collateral_infos[collateral_type].single_price_querier.get_current_feed(sender=self.name)
        spot = 0
        if feed.feed_is_live:
            spot = feed.spot_price / self.collateral_infos[collateral_type].liquidation_ratio
        self.bank.set_spot_price(collateral_type, spot)

    # -------------------------------------------------------
    # ------------------------ Setters ----------------------
    # -------------------------------------------------------

    # Turns the querier off if the sender [caller of the function]
    # has authorization access.
    # [spot.sol] Replicates cage
    def turn_querier_off(self, sender: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")

    # -------------------------------------------------------
    # ---------- Granting/Removing Authorization ------------
    # -------------------------------------------------------

    # Grants authorization for a specific user if the sender [caller
    # of the function] has authorization access.
    # [spot.sol] Replicates rely(address guy) external auth
    def grant_authorization(self, sender: User, new_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.authorized_users[new_user] = True

    # Removes authorization for a specific user if the sender [caller
    # of the function] has authorization access.
    # [spot.sol] Replicates deny(address guy) external auth
    def remove_authorization(self, sender: User, old_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.authorized_users[old_user] = False
