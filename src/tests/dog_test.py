import unittest

from src.liquidation_module.abacus import LinearDecrease
from src.liquidation_module.clip import LiquidationModule, AuctionCollateral, AuctionManager
from src.version0.all_price_querier import AllCollateralPriceQuerier, CollateralInfoForQuerying
from src.version0.bank_vat import Bank, Loan, CollateralInfo
from src.version0.primitives import User, Ticker
from src.version0.single_price_querier import SingleCollateralPriceQuerier, Feed


class TestStatics(unittest.TestCase):
    def test_debt_safe(self):
        self.assertTrue(LiquidationModule.debt_safe(1.0, 2.0, 3.0, 1.0))
        self.assertFalse(LiquidationModule.debt_safe(-1.0, 2.0, 1.0, 1.0))
        self.assertFalse(LiquidationModule.debt_safe(3.0, 1.0, 2.0, 1.0))

    def test_auction_not_dusty(self):
        self.assertTrue(LiquidationModule.auction_not_dusty(100.0, 0.1, 10.0))
        self.assertTrue(LiquidationModule.auction_not_dusty(100.0, 0.5, 1.0))
        self.assertFalse(LiquidationModule.auction_not_dusty(100.0, 0.001, 10.0))

    def test_auction_not_null(self):
        self.assertTrue(LiquidationModule.auction_not_null(0.1))
        self.assertFalse(LiquidationModule.auction_not_null(0.0))
        self.assertFalse(LiquidationModule.auction_not_null(-0.1))

    def test_no_overflow(self):
        self.assertTrue(LiquidationModule.no_overflow(1.0, 1.0))
        self.assertFalse(LiquidationModule.no_overflow(2**256, 1.0))
        self.assertFalse(LiquidationModule.no_overflow(2**256, 2**256))
        self.assertTrue(LiquidationModule.no_overflow(-0.1, -0.1))


class TestDog(unittest.TestCase):
    user1 = User("Jimmy")
    user2 = User("Jerry")
    user3 = User("Johnny")
    ticker1 = Ticker("ETH")
    feed1 = Feed(20.0, True)
    feed2 = Feed(21.0, True)
    singleQuerier1 = SingleCollateralPriceQuerier(user1, True, user1, 1.0, feed1,
                                                  feed2, {user1: True, user2: True, user3: False},
                                                  {user1: True, user2: False, user3: False})
    queryInfo1 = CollateralInfoForQuerying(singleQuerier1, 0.1)
    ticker2 = Ticker("BTC")
    feed3 = Feed(10.0, True)
    feed4 = Feed(11.0, True)
    singleQuerier2 = SingleCollateralPriceQuerier(user1, True, user1, 1.0, feed3, feed4,
                                                  {user1: True, user2: True, user3: False},
                                                  {user1: True, user2: False, user3: False})
    queryInfo2 = CollateralInfoForQuerying(singleQuerier2, 0.2)
    approved_loan_modifiers = {user1: {user1: True, user2: False, user3: False},
                               user2: {user1: True, user2: True, user3: False},
                               user3: {user1: False, user2: True, user3: False}}
    loans = {ticker1: {user1: Loan(1.0, 1.0), user2: Loan(0.0, 0.0), user3: Loan(2.0, 1.0)},
             ticker2: {user1: Loan(0.0, 0.0), user2: Loan(0.5, 1.0), user3: Loan(100.0, 20.0)}}
    collateral_infos = {ticker1: CollateralInfo(1.0, 2.0, 30.0, 0.1, 1.0),
                        ticker2: CollateralInfo(2.0, 21.0, 200.0, 0.5, 5.0)}
    who_owns_collateral = {ticker1: {user1: 2.0, user2: 0.0, user3: 1.0},
                           ticker2: {user1: 0.0, user2: 2.0, user3: 200.0}}
    who_owns_debt = {user1: 20, user2: 5, user3: 400}
    seized_debt = {user1: 0.0, user2: 0.0, user3: 20.0}
    bank = Bank(loans, collateral_infos, True, 23.0, 500.0, approved_loan_modifiers,
                who_owns_collateral, who_owns_debt, seized_debt)
    queryingCollaterals = {ticker1: queryInfo1, ticker2: queryInfo2}
    allQuerier = AllCollateralPriceQuerier(user1, queryingCollaterals, bank, True,
                                           {user1: True, user2: False, user3: False})
    auctionCollateral1 = AuctionCollateral(user1, 1.0, 300.0, 1.0)
    auctionCollateral2 = AuctionCollateral(user1, 2.0, 300.0, 1.0)
    liquidation_module = LiquidationModule(bank, {ticker1: auctionCollateral1, ticker2: auctionCollateral2},
                                           , 200.0, 1.0, allQuerier)
    auction_manager = AuctionManager(bank, allQuerier, user1, LinearDecrease(3000.0), )


if __name__ == '__main__':
    print("Testing...")
    unittest.main()
    print("All tests passed.")