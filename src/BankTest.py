import unittest
from bank import Bank
from bank import CollateralInfo
from bank import Loan


class TestStatics(unittest.TestCase):
    def test_debt_has_decreased(self):
        self.assertTrue(Bank.debt_has_decreased(-0.5))
        self.assertFalse(Bank.debt_has_decreased(1))
        self.assertTrue(Bank.debt_has_decreased(0))

    def test_acceptable_loan(self):
        collateral_info = CollateralInfo(1.0, 1.0, 2.0, 0.1, 0.01)
        loan = Loan(3.0, 1.0)
        self.assertTrue(Bank.acceptable_loan(-0.1, 0.1, collateral_info, loan))


if __name__ == '__main__':
    print("Testing...")
    unittest.main()
    print("All tests passed.")
