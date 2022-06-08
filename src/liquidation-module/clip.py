from src.primitives import Ticker, User
from src.bank_vat import Bank
from typing import Dict
from dog import LiquidationModule, AuctionCollateral


class Sale:
    def __init__(self, pos, tab, collateral_address: Ticker, liquidated: User,
                 auction_start_time, auction_start_price: float, spotter):
        self.pos = pos
        self.tab = tab
        self.collateral_address = collateral_address
        self.liquidated = liquidated
        self.auction_start_time = auction_start_time
        self.auction_start_price = auction_start_price
        self.spotter = spotter


class AuctionManager:
    def __init__(self, bank: Bank, spotter, liquidation_module: LiquidationModule, auction_collateral: AuctionCollateral):
        self.bank = bank
        self.spotter = spotter
        self.liquidation_module = liquidation_module
        self.auction_collateral = auction_collateral

    def getPrice(self, price):
        collateral = spotter.collaterals[self.collateral_address]
