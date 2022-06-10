from src.version0.primitives import Ticker, User
from src.version0.bank_vat import Bank
from typing import Dict
import datetime
from dog import LiquidationModule


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
    def __init__(self, bank: Bank, spotter, auction_recipient, price_calculator,
                 liquidation_module: LiquidationModule, auction_collateral_address: Ticker):
        # vat
        self.bank = bank
        # spotter
        self.spotter = spotter
        # dog
        self.liquidation_module = liquidation_module
        # vow
        self.auction_recipient = auction_recipient
        # AbacusLike (one of the price calculators in abacus.py)
        self.price_calculator = price_calculator
        # ilk
        self.auction_collateral_address = auction_collateral_address
        # buf
        # note that this is not used here because top/starting_price is not calculated
        self.price_factor = 1
        # tail
        self.time_before_reset = datetime.timedelta(days=1)
        # cusp
        self.percent_drop_before_reset = -0.1
        # chip
        self.percent_incentive = 0.01
        # tip
        self.flat_incentive = 20
        # kicks
        self.total_auctions = 0
        # sales
        self.sales = {}  # dictionary of integer indices to Sale
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

    def get_starting_price(self):
        single_price_querier = self.spotter.collateral_infos[self.auction_collateral_address].single_price_querier
        return single_price_querier.get_current_feed(self.auction_recipient)

    def start_auction(self, tab: float, collateral_amount: float,
                      receiver_of_leftover_collateral: User, receiver_of_incentives: User):
        starting_price = self.get_starting_price()
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

    # current_time is a stand-in for block.timestamp, although these are not really the same thing
    def auction_status(self, start_time: datetime.datetime, start_price):
        price = self.price_calculator.price(start_price, datetime.datetime.now() - start_time)
        auction_needs_redo = datetime.datetime.now() - start_time > self.time_before_reset or price/start_price < self.percent_drop_before_reset
        return auction_needs_redo, price

    def reset_auction(self, auction_id: int, receiver_of_incentives: User):
        start_time = self.sales[auction_id].auction_start_time
        start_price = self.sales[auction_id].auction_start_price
        tab = self.sales[auction_id].tab
        collateral_to_sell = self.sales[auction_id].collateral_to_sell
        feed_price = self.get_starting_price()
        new_start_price = feed_price * self.price_factor
        redo, price = self.auction_status(start_time, start_price)
        if redo and new_start_price > 0:
            self.sales[auction_id].auction_start_time = datetime.datetime.now()
            self.sales[auction_id].auction_start_price = new_start_price
            if self.percent_incentive > 0 or self.flat_incentive > 0:
                if tab >= self.minimum_target and collateral_to_sell * feed_price >= self.minimum_target:
                    incentive = self.flat_incentive + self.percent_incentive * tab
                    self.bank.add_debt(self.auction_recipient, receiver_of_incentives, incentive)


