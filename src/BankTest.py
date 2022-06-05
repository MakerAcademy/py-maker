import unittest
from bank_vat import Bank
from bank_vat import CollateralInfo
from bank_vat import Loan


class TestStatics(unittest.TestCase):
    def test_debt_has_decreased(self):
        self.assertTrue(Bank.debt_has_decreased(-0.5))
        self.assertFalse(Bank.debt_has_decreased(1))
        self.assertTrue(Bank.debt_has_decreased(0))

    def test_acceptable_loan(self):
        collateral_info = CollateralInfo(1.0, 1.0, 2.0, 0.1, 1.0)
        loan = Loan(3.0, 1.0)
        self.assertTrue(Bank.acceptable_loan(-0.1, 0.1, collateral_info, loan))
        loan = Loan(3.0, 100.0)
        self.assertFalse(Bank.acceptable_loan(0.1, 0.1, collateral_info, loan))
        self.assertFalse(Bank.acceptable_loan(-0.1, -0.1, collateral_info, loan))
        self.assertTrue(Bank.acceptable_loan(0, 0, collateral_info, loan))
        loan = Loan(3.0, 1.0)
        self.assertTrue(Bank.acceptable_loan(1.0, 1.0, collateral_info, loan))

    def test_debt_safe_loan(self):
        collateral_info = CollateralInfo(1.0, 1.0, 2.0, 0.1, 0.2)
        loan = Loan(3.0, 0.0)
        self.assertTrue(Bank.debt_safe_loan(loan, 0.0, collateral_info))
        loan = Loan(3.0, 2.0)
        self.assertTrue(Bank.debt_safe_loan(loan, 1.0, collateral_info))
        loan = Loan(1.0, 1.0)
        collateral_info = CollateralInfo(1.0, 1.0, 1.0, 5.0, 1.0)
        self.assertFalse(Bank.debt_safe_loan(loan, 1.0, collateral_info))


class TestBank(unittest.TestCase):
    def test_below_max_debt(self):
        approved_loan_modifiers = [[True, False], [True, True]]
        loans = [Loan(1.0, 1.0), Loan(0.5, 1.0)]
        collateral_infos = [CollateralInfo(1.0, 1.0, 2.0, 0.1, 1.0), CollateralInfo(2.0, 1.0, 1.0, 0.5, 5.0)]
        who_owns_collateral = [[1.0], [0.5]]
        who_owns_debt = [0.4, 0.3]
        bank = Bank(loans, collateral_infos, False, 0.7, 1.0, approved_loan_modifiers,
                    who_owns_collateral, who_owns_debt)
        self.assertTrue(bank.below_max_debt(0.1, collateral_infos[0]))


if __name__ == '__main__':
    print("Testing...")
    unittest.main()
    print("All tests passed.")
