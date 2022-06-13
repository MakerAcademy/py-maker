import unittest
from src.version0.bank_vat import Bank
from src.version0.bank_vat import CollateralInfo
from src.version0.bank_vat import Loan
from src.version0.primitives import User, Ticker


class TestStatics(unittest.TestCase):
    def test_debt_has_decreased(self):
        self.assertTrue(Bank.debt_has_decreased(delta_debt_amt=-0.5))
        self.assertFalse(Bank.debt_has_decreased(delta_debt_amt=1))
        self.assertTrue(Bank.debt_has_decreased(delta_debt_amt=0))

    def test_acceptable_loan(self):
        collateral_info = CollateralInfo(
            safe_spot_price=0.1,
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

    def test_requirements(self):
        user1 = User("Jimmy")
        user2 = User("Jerry")
        user3 = User("Johnny")
        ticker1 = Ticker("ETH")
        ticker2 = Ticker("BTC")
        approved_loan_modifiers = {user1: {user1: True, user2: False, user3: False},
                                   user2: {user1: True, user2: True, user3: False},
                                   user3: {user1: False, user2: True, user3: True}}
        loans = {ticker1: {user1: Loan(1.0, 1.0), user2: Loan(0.0, 0.0), user3: Loan(2.0, 1.0)},
                 ticker2: {user1: Loan(0.0, 0.0), user2: Loan(0.5, 1.0), user3: Loan(100.0, 20.0)}}
        collateral_infos = {ticker1: CollateralInfo(1.0, 2.0, 30.0, 0.1, 1.0),
                            ticker2: CollateralInfo(2.0, 21.0, 200.0, 0.5, 5.0)}
        who_owns_collateral = {ticker1: {user1: 2.0, user2: 0.0, user3: 1.0},
                               ticker2: {user1: 0.0}, user2: 2.0, user3: 200.0}
        who_owns_debt = {user1: 20, user2: 5, user3: 400}
        seized_debt = {user1: 0.0, user2: 0.0, user3: 20.0}
        bank = Bank(loans, collateral_infos, True, 23.0, 500.0, approved_loan_modifiers,
                    who_owns_collateral, who_owns_debt, seized_debt)
        self.assertTrue(bank.below_max_debt(1.0, bank.collateral_infos[ticker1]))


if __name__ == '__main__':
    print("Testing...")
    unittest.main()
    print("All tests passed.")
