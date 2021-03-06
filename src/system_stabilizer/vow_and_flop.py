# vow and flop are in the same file due to circular dependency issues that do not exist in Solidity
import time

from src.version0.bank_vat import Bank
from typing import Dict


# vow
from src.version0.primitives import User


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
        # Ash in dss
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
        # address of this contract
        self.address = User(str(hash(self)))
        self.bank.add_contract_address(self.address)

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

    # vow.heal in dss
    def settle_debt(self, sender: User, settled_amount: float):
        if settled_amount <= self.bank.who_owns_debt[self.address]:
            if settled_amount <= self.bank.seized_debt[self.address] - self.total_queued_debt - self.on_auction_debt:
                self.bank.settle_debt(sender, settled_amount)

    # vow.kiss in dss
    def settle_auction_debt(self, sender: User, settled_amount: float):
        if settled_amount < self.on_auction_debt:
            if settled_amount <= self.bank.who_owns_debt[self.address]:
                self.on_auction_debt -= settled_amount
                self.bank.settle_debt(sender, settled_amount)

    # vow.flop in dss
    def debt_auction(self, id):
        if (self.deficit_fixed_bid_size <= self.bank.seized_debt[self.address]
                - self.total_queued_debt - self.on_auction_debt):
            if self.bank.who_owns_debt[self.address] == 0:
                self.on_auction_debt += self.deficit_fixed_bid_size
                # return? probably an emit function
                id = self.deficit_auction_manager.kick(self.address,
                                                       self.deficit_initial_lot_size, self.deficit_fixed_bid_size)

    # vow.flap in dss
    def surplus_auction(self, id):
        if (self.bank.who_owns_debt[self.address] >=
                self.bank.seized_debt[self.address] + self.surplus_fixed_lot_size + self.surplus_buffer):
            if self.bank.seized_debt[self.address] - self.total_queued_debt - self.on_auction_debt:
                id = self.surplus_auction_manager.kick(self.surplus_fixed_lot_size, 0)

    # vow.cage in dss
    def shutdown(self):
        if self.live:
            self.live = False
            self.total_queued_debt = 0
            self.on_auction_debt = 0
            self.surplus_auction_manager.shutdown()
            self.deficit_auction_manager.shutdown()
            self.bank.settle_debt(self.address, min(self.bank.who_owns_debt[self.address],
                                                    self.bank.seized_debt[self.address]))