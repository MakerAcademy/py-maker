# vow and flop are in the same file due to circular dependency issues that do not exist in Solidity
import time

from src.version0.bank_vat import Bank
from typing import Dict


# vow
class Stabilizer:
    def __init__(self, bank: Bank, surplus_auction_manager, deficit_auction_manager, debt_queue: Dict[float, float],
                 total_queued_debt: float, on_auction_debt: float, deficit_auction_delay: float,
                 deficit_initial_lot_size: float, deficit_fixed_bid_size: float, surplus_fixed_lot_size: float,
                 surplus_buffer: float, live: bool):
        # vat in dss
        self.bank = bank
        # flapper in dss
        self.surplus_auction_manager = surplus_auction_manager
        # flopper in dss
        self.deficit_auction_manager = deficit_auction_manager
        # sin in dss
        self.debt_queue = debt_queue
        # Sin in dss
        self.total_queued_debt = total_queued_debt
        # ash in dss
        self.on_auction_debt = on_auction_debt
        # wait in dss
        self.deficit_auction_delay = deficit_auction_delay
        # dump in dss
        self.deficit_initial_lot_size = deficit_initial_lot_size
        # sump in dss
        self.deficit_fixed_bid_size = deficit_fixed_bid_size
        # bump in dss
        self.surplus_fixed_lot_size = surplus_fixed_lot_size
        # hump in dss
        self.surplus_buffer = surplus_buffer
        # live in dss
        self.live = live

    # vow.fess in dss
    def add_to_debt_queue(self, debt_amount: float):
        now = time.time()
        self.debt_queue[now] = debt_amount
        self.total_queued_debt += debt_amount

    # vow.flog in dss
    def remove_from_debt_queue(self, timestamp: float):
        # if statement is equivalent to require(add(era, wait) <= now, "Vow/wait-not-finished"); in dss
        if timestamp + self.deficit_auction_delay > time.time():
            self.total_queued_debt -= self.debt_queue[timestamp]
            self.debt_queue[timestamp] = 0

