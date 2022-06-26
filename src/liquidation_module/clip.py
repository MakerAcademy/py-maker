from src.version0.primitives import Ticker, User, get_current_blocktime
from src.version0.bank_vat import Bank
from typing import Dict
from src.liquidation_module import abacus
from src.version0.all_price_querier import AllCollateralPriceQuerier
# dog.py

# ilk structure within dog.sol
class AuctionCollateral:
    def __init__(self, liquidator: User, liquidation_penalty: float, max_auction_cost: float, auction_cost: float):
        # an address pointing to the liquidating user
        self.liquidator = liquidator
        # current liquidation penalty
        self.liquidation_penalty = liquidation_penalty
        # max DAI needed to cover debt and fees of active auctions per collateral
        self.max_auction_cost = max_auction_cost
        # DAI needed to cover debt and fees of active auctions per collateral
        self.auction_cost = auction_cost

# dog contract in dss
class LiquidationModule:
    def __init__(self, bank: Bank, collaterals: Dict[Ticker, AuctionCollateral],
                 debt_engine, max_auction_cost: float, auction_cost: float, spotter: AllCollateralPriceQuerier):
        # dog module takes in a vat/bank
        self.bank = bank
        # dictionary of collateral addresses to AuctionCollateral
        self.collaterals = collaterals
        # debt engine module / vow in dss
        self.debt_engine = debt_engine
        # max DAI needed to cover debt and fees of active auctions
        self.max_auction_cost = max_auction_cost
        # DAI needed to cover debt and fees of active auctions
        self.auction_cost = auction_cost
        # default placeholder abacus for handling the price calculation math in auctions
        self.abacus = abacus.LinearDecrease(20)
        # spotter used in liquidation
        self.spotter = spotter

    # getter function to return the liquidation penalty for the collateral with the specified Ticker
    # chop function in dss
    def get_liquidation_penalty(self, ticker: Ticker):
        return self.collaterals[ticker].liquidation_penalty

    # require(spot > 0 && mul(ink, spot) < mul(art, rate), "Dog/not-unsafe");
    @staticmethod
    def debt_safe(spot_price: float, collateral_amount: float, debt_amount: float, interest_rate: float):
        return spot_price > 0 and collateral_amount * spot_price < debt_amount * interest_rate

    # require(Hole > Dirt & & milk.hole > milk.dirt, "Dog/liquidation-limit-hit");
    def liquidation_limit_not_exceeded(self, collateral_max_auction_cost: float, collateral_auction_cost: float):
        return self.max_auction_cost > self.auction_cost and collateral_max_auction_cost > collateral_auction_cost

    # require(mul(dart, rate) >= dust, "Dog/dusty-auction-from-partial-liquidation");
    @staticmethod
    def auction_not_dusty(delta_debt_amount: float, interest_rate: float, min_debt_amount: float):
        return delta_debt_amount * interest_rate >= min_debt_amount

    # require(dink > 0, "Dog/null-auction");
    @staticmethod
    def auction_not_null(delta_collateral_amount: float):
        return delta_collateral_amount > 0

    # probably don't need to make this check in python
    # require(dart <= 2**255 && dink <= 2**255, "Dog/overflow");
    @staticmethod
    def no_overflow(delta_debt_amount: float, delta_collateral_amount: float):
        return delta_debt_amount <= 2**255 and delta_collateral_amount <= 2**255

    # compiling all requirements for liquidate function into one boolean
    def liquidate_requirements(self, spot_price: float, collateral_amount: float, debt_amount: float,
                               interest_rate: float, collateral_max_auction_cost: float, collateral_auction_cost: float,
                               delta_collateral_amount: float, delta_debt_amount: float):
        return self.debt_safe(spot_price, collateral_amount, debt_amount, interest_rate) and \
               self.liquidation_limit_not_exceeded(collateral_max_auction_cost, collateral_auction_cost) and \
               self.auction_not_null(delta_collateral_amount) and \
               self.no_overflow(delta_debt_amount, delta_collateral_amount)

    # function to liquidate a loan and start a Dutch auction
    # sells collateral for DAI
    # address_to_reward is the loan address to give the liquidation reward to, if any
    # bark function in dss
    def liquidate(self, ticker: Ticker, user: User, address_to_reward: User):
        # vat.urns(ilk, urn)
        loan = self.bank.loans[ticker][user]
        # ink
        collateral_amount = loan.collateral_amt
        # art
        debt_amount = loan.debt_amt
        # milk
        auction_collateral = self.collaterals[ticker]
        # rate
        interest_rate = self.bank.collateral_infos[ticker].interest_rate
        # spot
        safe_spot = self.bank.collateral_infos[ticker].safe_spot_price
        # dust
        min_debt_amount = self.bank.collateral_infos[ticker].min_debt_amt
        # uint256 room = min(Hole - Dirt, milk.hole - milk.dirt);
        cost_range = min(self.max_auction_cost - self.auction_cost,
                         auction_collateral.max_auction_cost - auction_collateral.auction_cost)
        # dart = min(art, mul(room, WAD) / rate / milk.chop);
        delta_debt_amount = min(debt_amount, cost_range/interest_rate/self.get_liquidation_penalty(ticker))
        if debt_amount > delta_debt_amount:
            passer = False
            if (debt_amount - delta_debt_amount) * interest_rate < min_debt_amount:
                # total liquidation to prevent falling below minimum debt amount
                delta_debt_amount = debt_amount
                passer = True
            if self.auction_not_dusty(delta_debt_amount, interest_rate, min_debt_amount) or passer:
                delta_collateral_amount = collateral_amount * delta_debt_amount / debt_amount
                if self.liquidate_requirements(safe_spot, collateral_amount, debt_amount, interest_rate,
                                               auction_collateral.max_auction_cost, auction_collateral.auction_cost,
                                               delta_collateral_amount, delta_debt_amount):
                    # grab
                    self.bank.seize_debt(ticker, user, auction_collateral.liquidator, self.debt_engine,
                                         -delta_collateral_amount, -delta_debt_amount)
                    due = delta_debt_amount * interest_rate
                    # vow.fess(due) in dss. function name will change when vow.py is written
                    self.debt_engine.fess(due)
                    tab = due * self.get_liquidation_penalty(ticker)
                    self.auction_cost += tab
                    auction_collateral.auction_cost += tab
                    # variable id is used in event emitting, spot.py is not yet written
                    auction = AuctionManager(self.bank, self.spotter, auction_collateral.liquidator,
                                             self.abacus, self, ticker).start_auction(tab, delta_collateral_amount,
                                                                                      user, address_to_reward)
                    # the dss code would emit a Bark event here, but events are not implemented in py-maker

    # digs function in dss
    def change_auction_cost(self, collateral_address: Ticker, amount: float):
        self.auction_cost -= amount
        self.collaterals[collateral_address].auction_cost -= amount


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
    def __init__(self, bank: Bank, spotter: AllCollateralPriceQuerier, auction_recipient: User, price_calculator,
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
        self.time_before_reset = 123456789
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

        self.address = User("AuctionManager: " + hex(id(self)))

        self.bank.add_contract_address(self.address)

    @staticmethod
    def auction_requirements(tab: float, collateral_amount: float,
                             receiver_of_leftover_collateral: User, starting_price: float):
        tab_nonzero = tab > 0
        collateral_nonzero = collateral_amount > 0
        receiver_valid = receiver_of_leftover_collateral.name != ''
        starting_nonzero = starting_price > 0
        return tab_nonzero and collateral_nonzero and receiver_valid and starting_nonzero

    def get_starting_price(self):
        single_price_querier = self.spotter.collateral_infos[self.auction_collateral_address].single_price_querier
        return single_price_querier.get_current_feed(self.auction_recipient).spot_price

    # kick function in dss
    def start_auction(self, tab: float, collateral_amount: float,
                      receiver_of_leftover_collateral: User, receiver_of_incentives: User):
        starting_price = self.get_starting_price()
        if self.auction_requirements(tab, collateral_amount, receiver_of_leftover_collateral, starting_price):
            self.total_auctions += 1
            self.active_auctions.append(self.total_auctions - 1)
            sale = Sale(self.total_auctions, tab, collateral_amount,
                        receiver_of_leftover_collateral, get_current_blocktime(), starting_price, self.spotter)
            self.sales[self.total_auctions - 1] = sale
            if self.percent_incentive > 0 or self.flat_incentive > 0:
                incentive = self.flat_incentive + self.percent_incentive * tab
                self.bank.add_debt(self.auction_recipient, receiver_of_incentives, incentive)
            # the dss would emit a Kick event at this point to document the start of the auction

    # current_time is a stand-in for block.timestamp, although these are not really the same thing
    def auction_status(self, start_time: float, start_price: float):
        price = self.price_calculator.price(start_price, get_current_blocktime() - start_time)
        auction_needs_redo = get_current_blocktime() - start_time > self.time_before_reset or \
            price/start_price < self.percent_drop_before_reset
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
            self.sales[auction_id].auction_start_time = get_current_blocktime()
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
                self.auction_collateral_address, self.sales[auction_id].tab + cost if
                self.sales[auction_id].collateral_to_sell == 0 else cost)
            if self.sales[auction_id].collateral_to_sell == 0:
                self.remove_auction(auction_id)
            elif self.sales[auction_id].tab == 0:
                # again not sure who the sender should be here
                self.bank.transfer_collateral(self.auction_collateral_address, self.address, self.address,
                                              self.sales[auction_id].liquidated,
                                              self.sales[auction_id].collateral_to_sell)
                self.remove_auction(auction_id)

    # remove function in dss
    def remove_auction(self, auction_id: int):
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
        self.minimum_target = min_debt * \
            self.liquidation_module.get_liquidation_penalty(self.auction_collateral_address)

    # yank function in dss
    def cancel_auction(self, auction_id: int, user_receiving_auction_collateral: User):
        self.liquidation_module.change_auction_cost(self.auction_collateral_address, self.sales[auction_id].tab)
        # not sure on sender here
        self.bank.transfer_collateral(self.auction_collateral_address, self.address, self.address,
                                      user_receiving_auction_collateral, self.sales[auction_id].collateral_to_sell)




