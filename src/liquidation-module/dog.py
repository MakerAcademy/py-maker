from src.primitives import Ticker, User
from src.bank_vat import Bank
from typing import Dict

# ilk structure within dog.sol
class AuctionCollateral:
    def __init__(self, liquidator: Ticker, liquidation_penalty: float, max_auction_cost: float, auction_cost: float):
        # an address pointing to a liquidator for a dictionary of {Ticker : liquidator}
        self.liquidator = liquidator
        # current liquidation penalty
        self.liquidation_penalty = liquidation_penalty
        # max DAI needed to cover debt and fees of active auctions per collateral
        self.max_auction_cost = max_auction_cost
        # DAI needed to cover debt and fees of active auctions per collateral
        self.auction_cost = auction_cost


# dog contract in dss
class LiquidationModule:
    def __init__(self, bank: Bank, collaterals: Dict[Ticker : AuctionCollateral]):
        # dog module takes in a vat/bank
        self.bank = bank
        # dictionary of collateral addresses to AuctionCollateral
        self.collaterals = collaterals

    # getter function to return the liquidation penalty for the collateral with the specified Ticker
    # chop function in dss
    def get_liquidation_penalty(self, address):
        return self.collaterals[address].liquidation_penalty

    # function to liquidate a loan and start a Dutch auction
    # sells collateral for DAI
    # address_to_reward is the loan address to give the liquidation reward to, if any
    # bark function in dss
    def liquidate(self, collateral_address, loan_address, address_to_reward):
        return "oh shit this one is long"
