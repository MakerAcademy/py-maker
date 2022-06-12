from primitives import Ticker, User
from typing import Dict
from bank_vat import Bank
from single_price_querier import SingleCollateralPriceQuerier


class SpotterCollateral:
    def __init__(self, price_feed: SingleCollateralPriceQuerier, liquidation_ratio: float):
        self.price_feed = price_feed
        self.liquidation_ratio = liquidation_ratio


class Spotter:
    def __init__(self, bank: Bank, collaterals: Dict[Ticker, SpotterCollateral], sender: User):
        self.bank = bank
        self.par = 10**27
        self.collaterals = collaterals
        self.sender = sender

    # file functions in dss
    def set_collateral_price_feed(self, ticker: Ticker, price_querier: SingleCollateralPriceQuerier):
        self.collaterals[ticker].price_feed = price_querier

    def set_spotter_par(self, new_par):
        self.par = new_par

    def set_collateral_liquidation_ratio(self, ticker: Ticker, new_ratio: float):
        self.collaterals[ticker].liquidation_ratio = new_ratio

    # should sender here be a sender that is taken in by the class, or a User address of the class itself?
    # poke function in dss
    def update_spot_price(self, collateral: Ticker):
        feed = self.collaterals[collateral].price_feed.get_current_feed(self.sender)
        feed_price = feed.spot_price
        live_feed = feed.feed_is_live
        spot_price = (feed_price * 10**9)/(self.par * self.collaterals[collateral].liquidation_ratio) if live_feed else 0
        self.bank.set_collateral_safe_spot_price(collateral, spot_price)
