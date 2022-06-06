from typing import Dict

from bank_vat import Bank
from primitives import Ticker
from singlePriceQuerier_osm import SingleCollateralPriceQuerier

# In dss, CollateralInfoSpot = Ilk struct
class CollateralInfoSpot:
    def __init__(self, price_feed: SingleCollateralPriceQuerier,
                 liquidation_ratio: float):
        # In dss, price_feed = pip
        self.price_feed = price_feed
        # In dss, liquidation_ratio = mat
        self.liquidation_ratio = liquidation_ratio

ONE = 10 ** 27

# In dss, CollateralPriceQuerier = Spotter1
class AllCollateralPriceQuerier:
    def __init__(self, collateral_infos: Dict[Ticker, CollateralInfoSpot],
                 bank: Bank, spotter_is_open: bool):
        # In dss, collateral_infos = ilks
        self.collateral_infos = collateral_infos
        # In dss, bank = vat
        self.bank = bank
        # In dss,
        self.par = ONE
        # In dss, spotter_is_open = live
        self.spotter_is_open = spotter_is_open

    def poke(self, collateral_type: Ticker):
        val, has = self.collateral_infos[collateral_type].price_feed.peek()
        spot = 0
        if has:
            spot = (10 ** 9) * val * (ONE) * ONE / self.par / self.collateral_infos[collateral_type].liquidation_ratio
        self.bank.set_spot_price(collateral_type, spot)