import unittest
from src.version0.bank_vat import Bank
from src.version0.bank_vat import CollateralInfo
from src.version0.bank_vat import Loan


class TestStatics(unittest.TestCase):
    def test_debt_has_decreased(self):
        self.assertTrue(Bank.debt_has_decreased(delta_debt_amt=-0.5))
        self.assertFalse(Bank.debt_has_decreased(delta_debt_amt=1))
        self.assertTrue(Bank.debt_has_decreased(delta_debt_amt=0))

    def test_acceptable_loan(self):
        collateral_info = CollateralInfo(
            safe_spot_price=20,
            total_debt_amt=0,
            max_debt_amt=1000,
            min_debt_amt=0.001,
            interest_rate=0.1
        )
        loan1 = Loan(
            collateral_amt=30,
            debt_amt=10)
        self.assertTrue(Bank.acceptable_loan(
            delta_debt_amt=-10,
            delta_collateral_amt=10,
            collateral_info=collateral_info,
            loan=loan1
        ))
        loan2 = Loan(
            collateral_amt=100,
            debt_amt=50)
        self.assertFalse(Bank.acceptable_loan(
            delta_debt_amt=10,
            delta_collateral_amt=-50,
            collateral_info=collateral_info,
            loan=loan2
        ))
        self.assertTrue(Bank.acceptable_loan(
            delta_debt_amt=0,
            delta_collateral_amt=0,
            collateral_info=collateral_info,
            loan=loan2
        ))

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
