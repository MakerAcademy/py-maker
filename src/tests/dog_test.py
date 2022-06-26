import unittest
from src.liquidation_module.clip import LiquidationModule, AuctionCollateral


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


if __name__ == '__main__':
    print("Testing...")
    unittest.main()
    print("All tests passed.")