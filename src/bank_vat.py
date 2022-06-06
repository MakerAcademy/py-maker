from typing import Dict
from primitives import Ticker, User
WAD = 10 ** 18

# vat.sol

# In dss, Loan = Urn
class Loan:
    # When a user creates a loan, they will put up a certain
    # amount of collateral (collateral_amt), and then take money
    # from the bank (debt_amt). These loans will always be
    # over-collateralized: the collateral_amt should always be
    # more than the debt_amt.
    def __init__(self, collateral_amt: float, debt_amt: float):
        # In dss, collateral_amt = ink
        self.collateral_amt = collateral_amt
        # In dss, debt_amt = art
        self.debt_amt = debt_amt

# In dss, CollateralInfo = Ilk
class CollateralInfo:
    # CollateralInfo will keep track of different metrics about a
    # certain collateral type. For example, the spot price of the
    # collateral (with a safety margin), the total debt (in loans)
    # that has been taken out against this particular collateral type,
    # the maximum debt that can be taken out against this particular
    # collateral type, and the interest rate for taking loans out
    # on this particular collateral type.
    def __init__(self, safe_spot_price: float, total_debt_amt: float,
                 max_debt_amt: float, min_debt_amt: float, interest_rate: float):
        # In dss, safe_spot_price = spot
        self.safe_spot_price = safe_spot_price
        # In dss, total_debt_amt = Art
        self.total_debt_amt = total_debt_amt
        # In dss, max_debt_amt = line
        self.max_debt_amt = max_debt_amt
        # In dss, min_debt_amt = dust
        self.min_debt_amt = min_debt_amt
        # In dss, interest_rate = rate
        self.interest_rate = interest_rate

# In the dss, Bank = Vat
class Bank:
    
    def __init__(self, loans: Dict[Ticker, Dict[User, Loan]],
                 collateral_infos: Dict[Ticker, CollateralInfo],
                 bank_is_open: bool, total_debt_issued : float,
                 max_debt_amount: float,
                 approved_loan_modifiers: Dict[User, Dict[User, bool]],
                 who_owns_collateral: Dict[Ticker, Dict[User, float]],
                 who_owns_debt: Dict[User, float]):
        # A nested dictionary that maps the ticker of the collateral type ("Eth" for example)
        # to a dictionary of loans per user for that collateral type.
        # ticker of collateral type [Ticker] -> name of user [User] -> Loan object [Loan]
        # In the dss, loans = urns
        self.loans = loans
        # Collateral infos is a dictionary that maps the ticker of a collateral type
        # to the CollateralInfo object.
        # collateral
        # In the dss, collateral_infos = ilks
        self.collateral_infos = collateral_infos
        # bank_is_open is True if it is open for business and False otherwise.
        # In the dss, bank_is_open = live
        self.bank_is_open = bank_is_open
        # total_debt_issued is an number that represents the total value of debt issued by
        # the bank to customers across all loans
        # In the dss, total_debt_issued = debt
        self.total_debt_issued = total_debt_issued
        # max_debt_amount is the maximum amount of debt that the bank is allowed to issue
        # In the dss, max_debt_amount = Line
        self.max_debt_amount = max_debt_amount
        # approved_loan_modifiers is a dictionary from users who are trying to modify a loan
        # to the owner of that loan to a bool (True if they can modify that user's loan, false
        # if not).
        # name of user [User] -> name of other user [User] -> bool
        # In the dss, approved_loan_modifiers = can
        self.approved_loan_modifiers = approved_loan_modifiers
        # who_owns_collateral is a dictionary that maps collateral types (represented by ticker)
        # to a user, to how much a user owns of that collateral type
        # In the dss, who_owns_collateral = gem
        self.who_owns_collateral = who_owns_collateral
        # who_owns_debt is a dictionary that maps users to the amount of debt they have
        # In the dss, who_owns_debt = dai
        self.who_owns_debt = who_owns_debt

    # This method checks whether the debt has decreased (the delta - change in - debt
    # is negative)
    @staticmethod
    def debt_has_decreased(delta_debt_amt: float) -> bool:
        return delta_debt_amt <= 0

    # This method checks whether the change in debt (delta_debt_amt) ensures that the debt
    # for that specific collateral type has not reached the max and that the bank's total debt
    # has not reached the max.
    # In the dss, this function is basically equivalent to the following require statement from the frob function
    # require(either(dart <= 0, both(_mul(ilk.Art, ilk.rate) <= ilk.line, debt <= Line)), "Vat/ceiling-exceeded");
    def below_max_debt(self, delta_debt_amt: float, collateral_info: CollateralInfo) -> bool:
        # In dss, equivalent to ilk.Art = _add(ilk.Art, dart) and then
        # _mul(ilk.Art, ilk.rate) <= ilk.line
        below_max_debt_per_collateral = (collateral_info.total_debt_amt +
                                         delta_debt_amt) * collateral_info.interest_rate <= collateral_info.max_debt_amt
        # In dss, equivalent to int dtab = _mul(ilk.rate, dart); and then
        # debt = _add(debt, dtab); and then debt <= Line
        below_max_system_debt = self.total_debt_issued + (delta_debt_amt * collateral_info.interest_rate) \
            <= self.max_debt_amount
        return below_max_debt_per_collateral and below_max_system_debt

    # This method checks whether a user of a loan either removed debt (meaning he owes less)
    # or whether the debt he added + interest is still less than the price of the collateral in USD.
    # In dss, it is equivalent to this require statement from the function frob
    # require(either(both(dart <= 0, dink >= 0), tab <= _mul(urn.ink, ilk.spot)), "Vat/not-safe");
    @staticmethod
    def acceptable_loan(delta_debt_amt, delta_collateral_amt, collateral_info, loan):
        # In dss, this is equivalent to both(dart <= 0, dink >= 0)
        added_collateral_removed_debt = delta_collateral_amt >= 0 >= delta_debt_amt
        # In dss, this is equivalent to urn.art = _add(urn.art, dart); and then
        # uint tab = _mul(ilk.rate, urn.art);
        users_tab = (loan.debt_amt + delta_debt_amt) * collateral_info.interest_rate
        # In dss, this is equivalent to urn.art = _add(urn.art, dart); and then
        # uint tab = _mul(ilk.rate, urn.art); and then tab <= _mul(urn.ink, ilk.spot)
        tab_is_safe = users_tab <= (loan.collateral_amt +
                                    delta_collateral_amt) * collateral_info.safe_spot_price
        return added_collateral_removed_debt or tab_is_safe

    # This method makes sure that the loan is getting less debt and more collateral (becoming a
    # smaller loan essentially), or the owner of the loan has consented for the sender to change
    # his balance.
    # In dss, this method is equivalent to this require statement from the function frob
    # require(either(both(dart <= 0, dink >= 0), wish(u, msg.sender)), "Vat/not-allowed-u");
    def sender_not_malicious(self, sender, user, delta_debt_amt, delta_collateral_amt):
        # In dss, this is equivalent to wish(u, msg.sender)
        approved_modifier = self.approved_loan_modifiers[sender][user]
        # In dss, this is equivalent to both(dart <= 0, dink >= 0)
        added_collateral_removed_debt = delta_collateral_amt >= 0 >= delta_debt_amt
        return approved_modifier or added_collateral_removed_debt

    # In dss, this method is equivalent to this require statement from the function frob
    # require(either(dink <= 0, wish(v, msg.sender)), "Vat/not-allowed-v");
    def sender_consent(self, user, sender, delta_collateral_amt):
        return delta_collateral_amt <= 0 or self.approved_loan_modifiers[sender][user]

    # In dss, this method is equivalent to this require statement from the function frob
    # require(either(dart >= 0, wish(w, msg.sender)), "Vat/not-allowed-w");
    def loan_user_consent(self, sender, delta_debt_amt):
        return delta_debt_amt >= 0 or self.approved_loan_modifiers[sender][sender]

    # In dss, this method is equivalent to this require statement from the function frob
    # require(either(urn.art == 0, tab >= ilk.dust), "Vat/dust");
    @staticmethod
    def debt_safe_loan(loan, delta_debt_amt, collateral_info):
        new_debt_amt = loan.debt_amt + delta_debt_amt
        return new_debt_amt == 0 or new_debt_amt * collateral_info.interest_rate >= collateral_info.min_debt_amt

    # This method is essentially all require statements from frob in dss grouped up into one function
    def acceptable_modification(self, delta_debt_amt, delta_collateral_amt, collateral_info, loan, sender, user):
        debt_amt_is_safe = self.debt_has_decreased(delta_debt_amt) or \
                             self.below_max_debt(delta_debt_amt, collateral_info)
        user_has_acceptable_loan = self.acceptable_loan(delta_debt_amt, delta_collateral_amt, collateral_info, loan)
        sender_not_malicious = self.sender_not_malicious(sender, user, delta_debt_amt, delta_collateral_amt)
        sender_consent = self.sender_consent(user, sender, delta_collateral_amt)
        loan_user_consent = self.loan_user_consent(sender, delta_debt_amt)
        debt_safe_loan = self.debt_safe_loan(loan, delta_debt_amt, collateral_info)
        return debt_amt_is_safe and sender_not_malicious and user_has_acceptable_loan and sender_consent \
            and loan_user_consent and debt_safe_loan and self.bank_is_open

    # In dss, this method is equivalent to frob
    def modify_loan(self, collateral_type, delta_collateral_amt, delta_debt_amt, user, sender):
        # In dss, this is equivalent to Ilk memory ilk = ilks[i];
        collateral_info = self.collateral_infos[collateral_type]
        # In dss, this is equivalent to Urn memory urn = urns[i][u];
        loan = self.loans[collateral_type][user]
        # this if statement basically ensures that all require statements within frob pass before moving along
        if self.acceptable_modification(delta_debt_amt, delta_collateral_amt, collateral_info, loan, sender, user):
            # In dss, this is equivalent to urn.ink = _add(urn.ink, dink);
            loan.collateral_amt += delta_collateral_amt
            # In dss, this is equivalent to urn.art = _add(urn.art, dart);
            loan.debt_amt += delta_debt_amt
            # In dss, this is equivalent to ilk.Art = _add(ilk.Art, dart);
            collateral_info.total_debt_amt += delta_debt_amt
            # In dss, this is equivalent to gem[i][v] = _sub(gem[i][v], dink);
            self.who_owns_collateral[collateral_type][sender] = self.who_owns_collateral[collateral_type][sender] - delta_collateral_amt
            # In dss, this is equivalent to dai[w]    = _add(dai[w],    dtab);
            self.who_owns_debt[user] = self.who_owns_debt[user] + (collateral_info.interest_rate * delta_debt_amt)
            # The below isn't needed because "=" copies by reference in python, not by value
            # In dss, this is equivalent to
            # self.collateral_infos[collateral_type] = collateral_info
            # In dss, this is equivalent to urns[i][u] = urn;
            # self.loans[collateral_type][user] = loan
            # In dss, this is equivalent to ilks[i]    = ilk;





    # @staticmethod
    # def loan_is_acceptable(collateral_info, loan):
    #     collateral_is_worthless = collateral_info.safe_spot_price < 0
    #     loan_is_collateralized = loan.collateral_amt * collateral_info.safe_spot_price > \
    #         loan.debt_amt * collateral_info.interest_rate
    #     return collateral_is_worthless or loan_is_collateralized
    #
    # def too_much_auction_debt(self, collateral_info):
    #     a = self.max_active_auction_debt < self.amt_active_auction_debt
    #     b = collateral_info.max_active_aution_debt < collateral_info.amt_active_aution_debt
    #     return a or b
    #
    # def inappropriate_time_to_liquidate(self, collateral_info, loan):
    #     loan_is_safe = self.loan_is_acceptable(collateral_info, loan)
    #     too_much_debt_in_auctions = self.too_much_auction_debt(collateral_info)
    #     return loan_is_safe or too_much_debt_in_auctions or self.bank_is_closed


    # In dss, this method is equivalent to slip
    def modify_collateral(self, user, collateral_type, delta_collateral_amount):
        self.who_owns_collateral[collateral_type][user] = \
            self.who_owns_collateral[collateral_type][user] + delta_collateral_amount

    # In dss, this method is equivalent to flux
    def transfer_collateral(self, collateral_type, sender, user1, user2, delta_collateral_amount):
        if self.approved_loan_modifiers[user1][sender]:
            self.who_owns_collateral[collateral_type][user1] -= delta_collateral_amount
            self.who_owns_collateral[collateral_type][user2] += delta_collateral_amount

    # In dss, this method is equivalent to slip
    def transfer_debt(self, sender, user1, user2, delta_debt_amount):
        if self.approved_loan_modifiers[user1][sender]:
            self.who_owns_debt[user1] -= delta_debt_amount
            self.who_owns_debt[user2] += delta_debt_amount

    # In dss, this is equivalent to this require statement in the fork function
    # require(both(wish(src, msg.sender), wish(dst, msg.sender)), "Vat/not-allowed");
    def sender_and_receiver_consent(self, sender, receiver):
        return self.approved_loan_modifiers[sender][receiver] and self.approved_loan_modifiers[receiver][sender]

    # In dss, this is equivalent to this require statement in the fork function
    # require(utab <= _mul(u.ink, i.spot), "Vat/not-safe-src");
    # require(vtab <= _mul(v.ink, i.spot), "Vat/not-safe-dst");
    @staticmethod
    def both_sides_safe(sender_tab, receiver_tab, sender_collateral_amount, receiver_collateral_amount, spot_price):
        sender_safe = sender_tab <= sender_collateral_amount * spot_price
        receiver_safe = receiver_tab <= receiver_collateral_amount * spot_price
        return sender_safe and receiver_safe

    # In dss, this is equivalent to this require statement in the fork function
    # require(either(utab >= i.dust, u.art == 0), "Vat/dust-src");
    # require(either(vtab >= i.dust, v.art == 0), "Vat/dust-dst");
    @staticmethod
    def check_minimum_debt(sender_tab, receiver_tab, minimum_debt, sender_debt_amount, receiver_debt_amount):
        sender_not_dusty = sender_tab >= minimum_debt or sender_debt_amount == 0
        receiver_not_dusty = receiver_tab >= minimum_debt or receiver_debt_amount == 0
        return sender_not_dusty and receiver_not_dusty

    def split_loan(self, sender, receiver, collateral_type, delta_debt_amount, delta_collateral_amount):
        sender_loan = self.loans[collateral_type][sender]
        receiver_loan = self.loans[collateral_type][receiver]
        collateral_info = self.collateral_infos[collateral_type]
        sender_collateral = sender_loan.collateral_amt - delta_collateral_amount
        sender_debt = sender_loan.debt_amt - delta_debt_amount
        receiver_collateral = receiver_loan.collateral_amt + delta_collateral_amount
        receiver_debt = receiver_loan.debt_amt + delta_debt_amount
        sender_tab = sender_debt * collateral_info.interest_rate
        receiver_tab = receiver_debt * collateral_info.interest_rate
        consent = self.sender_and_receiver_consent(sender, receiver)
        safe = self.both_sides_safe(sender_tab, receiver_tab, sender_collateral, receiver_collateral,
                                    collateral_info.safe_spot_price)
        minimum_achieved = self.check_minimum_debt(sender_tab, receiver_tab, collateral_info.min_debt_amt, sender_debt,
                                                   receiver_debt)
        if consent and safe and minimum_achieved:
            self.loans[collateral_type][sender].collateral_amt = sender_collateral
            self.loans[collateral_type][sender].debt_amt = sender_debt
            self.loans[collateral_type][receiver].collateral_amt = receiver_collateral
            self.loans[collateral_type][receiver].debt_amt = receiver_debt

    # In dss, this is basically equivalent to the following line
    # if (what == "spot") ilks[ilk].spot = data;
    # from the  function file(bytes32 ilk, bytes32 what, uint data) external auth {
    def set_spot_price(self, collateral_type: Ticker, spot_price: float):
        self.collateral_infos[collateral_type].safe_spot_price = spot_price


    # @staticmethod
    # def loan_is_acceptable(collateral_info, loan):
    #     collateral_is_worthless = collateral_info.safe_spot_price < 0
    #     loan_is_collateralized = loan.collateral_amt * collateral_info.safe_spot_price > \
    #         loan.debt_amt * collateral_info.interest_rate
    #     return collateral_is_worthless or loan_is_collateralized
    #
    # def too_much_auction_debt(self, collateral_info):
    #     a = self.max_active_auction_debt < self.amt_active_auction_debt
    #     b = collateral_info.max_active_aution_debt < collateral_info.amt_active_aution_debt
    #     return a or b
    #
    # def inappropriate_time_to_liquidate(self, collateral_info, loan):
    #     loan_is_safe = self.loan_is_acceptable(collateral_info, loan)
    #     too_much_debt_in_auctions = self.too_much_auction_debt(collateral_info)
    #     return loan_is_safe or too_much_debt_in_auctions or self.bank_is_closed
    #
    # def change_collateral_rate(self, collateral_type, u, new_rate):
    #     if self.bank_is_open:
    #         self.collateral_infos[collateral_type]
    #     pass
