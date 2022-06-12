from src.version0.primitives import Ticker, User
from src.version0.bank_vat import Bank
from typing import Dict
import datetime
from dog import LiquidationModule
from src.version0.spot import Spotter


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
    def __init__(self, bank: Bank, spotter: Spotter, auction_recipient, price_calculator,
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

        self.address = User(hex(id(self)))

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

    # kick function in dss
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

    # redo function in dss
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

    # take function in dss
    def buy_collateral(self, auction_id: int, collateral_limit: float, max_price: float, receiver_of_collateral: User):
        user = self.sales[auction_id].liquidator
        start_time = self.sales[auction_id].auction_start_time
        start_price = self.sales[auction_id].auction_start_price
        tab = self.sales[auction_id].tab
        collateral_to_sell = self.sales[auction_id].collateral_to_sell
        redo, price = self.auction_status(start_time, start_price)
        if (not redo) and max_price >= price:
            purchased = min(collateral_to_sell, collateral_limit)
            cost = purchased * price
            if cost > tab:
                cost = tab
                purchased = cost / price
            elif cost < tab and purchased < collateral_to_sell:
                if tab - cost < self.minimum_target:
                    if tab <= self.minimum_target:
                        return
                    else:
                        cost = tab - self.minimum_target
                        purchased = cost / price
            self.sales[auction_id].tab = tab - cost
            self.sales[auction_id].collateral_to_sell = collateral_to_sell - purchased
            # not certain on who the sender is for this transfer, and need to replicate functionality of address(this)
            # pass in address(this) on creation? use memory address of contract as a stand in?
            # implemented for now as hex code of memory id, which should be unique between different
            # instances of the same class, but the account associated with that address never actually receives
            # collateral or debt to transfer
            self.bank.transfer_collateral(self.auction_collateral_address, receiver_of_collateral,
                                          self.address, receiver_of_collateral, purchased)
            # I don't know what this does
            # if (data.length > 0 & & who != address(vat) & & who != address(dog_)) {
            # ClipperCallee(who).clipperCall(msg.sender, owe, slice, data);
            # }

            self.bank.transfer_debt(receiver_of_collateral, receiver_of_collateral, self.auction_recipient, cost)
            self.liquidation_module.change_auction_cost(
                self.auction_collateral_address, self.sales[auction_id].tab + cost if self.sales[auction_id].collateral_to_sell == 0 else cost)
            if self.sales[auction_id].collateral_to_sell == 0:
                self.remove_auction(auction_id)
            elif self.sales[auction_id].tab == 0:
                # again not sure who the sender should be here
                self.bank.transfer_collateral(self.auction_collateral_address, self.address, self.address,
                                              self.sales[auction_id].liquidated,
                                              self.sales[auction_id].collateral_to_sell)
                self.remove_auction(auction_id)

    # remove function in dss
    def remove_auction(self, auction_id):
        moved_auction = self.active_auctions[self.total_auctions - 1]
        if auction_id != moved_auction:
            index = self.sales[auction_id].index
            self.active_auctions[index] = moved_auction
            self.active_auctions.remove(self.total_auctions - 1)
            self.sales[moved_auction].index = index
        del self.sales[auction_id]

    def get_auction_count(self):
        return self.total_auctions

    def get_active_auctions(self):
        return self.active_auctions

    def update_minimum_target(self):
        min_debt = self.bank.collateral_infos[self.auction_collateral_address].min_debt_amt
        self.minimum_target = min_debt * self.liquidation_module.get_liquidation_penalty(self.auction_collateral_address)

    # yank function in dss
    def cancel_auction(self, auction_id: int, user_receiving_auction_collateral: User):
        self.liquidation_module.change_auction_cost(self.auction_collateral_address, self.sales[auction_id].tab)
        # not sure on sender here
        self.bank.transfer_collateral(self.auction_collateral_address, self.address, self.address,
                                      user_receiving_auction_collateral, self.sales[auction_id].collateral_to_sell)
