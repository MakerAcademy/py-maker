from src.version0.primitives import Ticker, User
from src.version0.bank_vat import Bank
from typing import Dict
import datetime
from dog import LiquidationModule, AuctionCollateral


class Sale:
    def __init__(self, index: int, tab: float, collateral_to_sell: float, liquidated: User,
                 auction_start_time, auction_start_price: float, spotter):
        self.index = index
        self.tab = tab
        self.collateral_to_sell = collateral_to_sell
        self.liquidated = liquidated
        self.auction_start_time = auction_start_time
        self.auction_start_price = auction_start_price
        self.spotter = spotter


class AuctionManager:
    def __init__(self, bank: Bank, spotter, auction_recipient,
                 liquidation_module: LiquidationModule, auction_collateral_address: Ticker,):
        # vat
        self.bank = bank
        # spotter
        self.spotter = spotter
        # dog
        self.liquidation_module = liquidation_module
        # vow
        self.auction_recipient = auction_recipient
        # ilk
        self.auction_collateral_address = auction_collateral_address
        # buf
        # note that this is not used here because top/starting_price is not calculated
        self.price_factor = 1
        # tail
        self.time_before_reset = 1  # it would be nice to insert a real time value here at some point
        # cusp
        self.percent_drop_before_reset = 0.1
        # chip
        self.percent_incentive = 0.01
        # tip
        self.flat_incentive = 20
        # kicks
        self.total_auctions = 0
        # sales
        self.sales = {}  # dictionary of indices to Sale
        # active
        self.active_auctions = []
        # this value is equivalent to chost in dss
        # chost is normally calculated asynchronously as auctions progress, but we calculate it once here
        self.minimum_target = bank.collateral_infos[auction_collateral_address].min_debt_amt * \
            liquidation_module.get_liquidation_penalty(auction_collateral_address)

    @staticmethod
    def auction_requirements(tab, collateral_amount, receiver_of_leftover_collateral, starting_price):
        tab_nonzero = tab > 0
        collateral_nonzero = collateral_amount > 0
        receiver_valid = receiver_of_leftover_collateral.name != ''
        starting_nonzero = starting_price > 0
        return tab_nonzero and collateral_nonzero and receiver_valid and starting_nonzero

    def start_auction(self, tab: float, collateral_amount: float,
                      receiver_of_leftover_collateral: User, receiver_of_incentives: User, starting_price: float):
        if self.auction_requirements(tab, collateral_amount, receiver_of_leftover_collateral, starting_price):
            self.total_auctions += 1
            self.active_auctions.append(self.total_auctions - 1)
            sale = Sale(self.total_auctions, tab, collateral_amount,
                        receiver_of_leftover_collateral, datetime.datetime.now(), starting_price, self.spotter)
            self.sales[self.total_auctions - 1] = sale
            if self.percent_incentive > 0 or self.flat_incentive > 0:
                incentive = self.flat_incentive + self.percent_incentive * tab
                self.bank.add_debt(self.auction_recipient, receiver_of_incentives, incentive)
            # the dss would emit a Kick event at this point to document the start of the auction
