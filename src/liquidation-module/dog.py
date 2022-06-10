from src.version0.primitives import Ticker, User
from src.version0.bank_vat import Bank
from typing import Dict
from clip import AuctionManager


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
                 debt_engine, max_auction_cost: float, auction_cost: float):
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

    # getter function to return the liquidation penalty for the collateral with the specified Ticker
    # chop function in dss
    def get_liquidation_penalty(self, ticker):
        return self.collaterals[ticker].liquidation_penalty

    # require(spot > 0 && mul(ink, spot) < mul(art, rate), "Dog/not-unsafe");
    @staticmethod
    def debt_safe(spot_price, collateral_amount, debt_amount, interest_rate):
        return spot_price > 0 and collateral_amount * spot_price < debt_amount * interest_rate

    # require(Hole > Dirt & & milk.hole > milk.dirt, "Dog/liquidation-limit-hit");
    def liquidation_limit_not_exceeded(self, collateral_max_auction_cost, collateral_auction_cost):
        return self.max_auction_cost > self.auction_cost and collateral_max_auction_cost > collateral_auction_cost

    # require(mul(dart, rate) >= dust, "Dog/dusty-auction-from-partial-liquidation");
    @staticmethod
    def auction_not_dusty(delta_debt_amount, interest_rate, min_debt_amount):
        return delta_debt_amount * interest_rate >= min_debt_amount

    # require(dink > 0, "Dog/null-auction");
    @staticmethod
    def auction_not_null(delta_collateral_amount):
        return delta_collateral_amount > 0

    # probably don't need to make this check in python
    # require(dart <= 2**255 && dink <= 2**255, "Dog/overflow");
    @staticmethod
    def no_overflow(delta_debt_amount, delta_collateral_amount):
        return delta_debt_amount <= 2**255 and delta_collateral_amount <= 2**255

    # compiling all requirements for liquidate function into one boolean
    def liquidate_requirements(self, spot_price, collateral_amount, debt_amount, interest_rate, collateral_max_auction_cost,
                               collateral_auction_cost, delta_collateral_amount, delta_debt_amount):
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
        range = min(self.max_auction_cost - self.auction_cost,
                    auction_collateral.max_auction_cost - auction_collateral.auction_cost)
        # dart = min(art, mul(room, WAD) / rate / milk.chop);
        delta_debt_amount = min(debt_amount, range/interest_rate/self.get_liquidation_penalty(ticker))  # this has WAD conversion in dss
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
                    id = AuctionManager(self.bank, spotter, auction_collateral.liquidator,
                                        abacus, self, ticker).kick(tab, delta_collateral_amount, user, address_to_reward)
                    # the dss code would emit a Bark event here, but events are not implemented in py-maker

    def change_auction_cost(self, collateral_address, amount):
        self.auction_cost -= amount
        self.collaterals[collateral_address].auction_cost -= amount
