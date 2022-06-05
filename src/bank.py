from typing import Dict

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

# Ticker represents the ticker of a certain collateral type, "ETH" for example
# In dss, ticker = bytes32 (kind of)
class Ticker:
    def __init__(self, tick: str):
        self.tick = tick

# User just represents the name of a user
# In dss, user = address (kind of)
class User:
    def __init__(self, name: str):
        self.name = name

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

    # This method checks whether
    def below_max_debt(self, delta_debt_amt: float, collateral_info: CollateralInfo):
        #
        below_max_debt_per_collateral = (collateral_info.total_debt_amt +
                                         delta_debt_amt) * collateral_info.interest_rate <= collateral_info.max_debt_amt
        #
        below_max_system_debt = self.total_debt_issued + (delta_debt_amt * collateral_info.interest_rate) \
            <= self.max_debt_amount
        return below_max_debt_per_collateral and below_max_system_debt

    @staticmethod
    def acceptable_loan(delta_debt_amt, delta_collateral_amt, collateral_info, loan):
        added_collateral_removed_debt = delta_collateral_amt >= 0 >= delta_debt_amt
        users_tab = (loan.debt_amt + delta_debt_amt) * collateral_info.interest_rate
        tab_is_safe = users_tab <= (loan.collateral_amt +
                                    delta_collateral_amt) * collateral_info.safe_spot_price
        return added_collateral_removed_debt or tab_is_safe

    def sender_not_malicious(self, sender, user, delta_debt_amt, delta_collateral_amt):
        approved_modifier = self.approved_loan_modifiers[sender][user]
        added_collateral_removed_debt = delta_collateral_amt >= 0 >= delta_debt_amt
        return approved_modifier or added_collateral_removed_debt

    def sender_consent(self, user, sender, delta_collateral_amt):
        return delta_collateral_amt <= 0 or self.approved_loan_modifiers[sender][user]

    def loan_user_consent(self, sender, delta_debt_amt):
        return delta_debt_amt >= 0 or self.approved_loan_modifiers[sender][sender]

    @staticmethod
    def debt_safe_loan(loan, delta_debt_amt, collateral_info):
        new_debt_amt = loan.debt_amt + delta_debt_amt
        return new_debt_amt == 0 or new_debt_amt * collateral_info.interest_rate >= collateral_info.min_debt_amt

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

    def modify_loan(self, collateral_type, delta_collateral_amt, delta_debt_amt, user, sender):
        collateral_info = self.collateral_infos[collateral_type]
        loan = self.loans[collateral_type][user]
        if self.acceptable_modification(delta_debt_amt, delta_collateral_amt, collateral_info, loan, sender, user):
            loan.collateral_amt += delta_collateral_amt
            loan.debt_amt += delta_debt_amt
            collateral_info.total_debt_amt += delta_debt_amt
            self.who_owns_collateral[collateral_type][sender] = self.who_owns_collateral[collateral_type][sender] - delta_collateral_amt
            self.who_owns_debt[user] = self.who_owns_debt[user] + (collateral_info.interest_rate * delta_debt_amt)

    @staticmethod
    def loan_is_acceptable(collateral_info, loan):
        collateral_is_worthless = collateral_info.safe_spot_price < 0
        loan_is_collateralized = loan.collateral_amt * collateral_info.safe_spot_price > \
            loan.debt_amt * collateral_info.interest_rate
        return collateral_is_worthless or loan_is_collateralized

    def too_much_auction_debt(self, collateral_info):
        a = self.max_active_auction_debt < self.amt_active_auction_debt
        b = collateral_info.max_active_aution_debt < collateral_info.amt_active_aution_debt
        return a or b

    def inappropriate_time_to_liquidate(self, collateral_info, loan):
        loan_is_safe = self.loan_is_acceptable(collateral_info, loan)
        too_much_debt_in_auctions = self.too_much_auction_debt(collateral_info)
        return loan_is_safe or too_much_debt_in_auctions or self.bank_is_closed


    def modify_collateral(self, user, collateral_type, delta_collateral_amount):
        self.who_owns_collateral[collateral_type][user] = \
            self.who_owns_collateral[collateral_type][user] + delta_collateral_amount

    def transfer_collateral(self, collateral_type, sender, receiver, delta_collateral_amount):
        if self.approved_loan_modifiers[sender][receiver]:
            self.who_owns_collateral[collateral_type][sender] -= delta_collateral_amount
            self.who_owns_collateral[collateral_type][receiver] += delta_collateral_amount

    def transfer_debt(self, sender, receiver, delta_debt_amount):
        if self.approved_loan_modifiers[sender][receiver]:
            self.who_owns_debt[sender] -= delta_debt_amount
            self.who_owns_debt[receiver] += delta_debt_amount

    def sender_and_receiver_consent(self, sender, receiver):
        return self.approved_loan_modifiers[sender][receiver] and self.approved_loan_modifiers[receiver][sender]

    @staticmethod
    def both_sides_safe(sender_tab, receiver_tab, sender_collateral_amount, receiver_collateral_amount, spot_price):
        sender_safe = sender_tab <= sender_collateral_amount * spot_price
        receiver_safe = receiver_tab <= receiver_collateral_amount * spot_price
        return sender_safe and receiver_safe

    def check_minimum_debt(self, sender_tab, receiver_tab, minimum_debt, sender_debt_amount, receiver_debt_amount):
        sender_not_dusty = sender_tab >= minimum_debt or sender_debt_amount == 0
        receiver_not_dusty = receiver_tab >= minimum_debt or receiver_debt_amount == 0
        return sender_not_dusty and receiver_not_dusty


    # def liquidate(self, collateral_type, user):
    #     loan = self.loans[collateral_type][user]
    #     collateral_info = self.collateral_infos[collateral_type]
    #
    #     if self.inappropriate_time_to_liquidate(collateral_info, loan):
    #         return
    #
    #     max_amt_to_liquidate = min(self.max_active_auction_debt - self.amt_active_auction_debt,
    #                                collateral_info.max_active_aution_debt - collateral_info.amt_active_aution_debt)
    #     # ??????? below
    #     dart = min(loan.debt_amt,
    #                max_amt_to_liquidate * WAD / collateral_info.interest_rate / collateral_info.liquidation_penalty)
    #
    #     if loan.debt_amt > dart:
    #         if (loan.debt_amt - dart) * collateral_info.interest_rate < collateral_info.dust:
    #             dart = loan.debt_amt
    #         elif not (dart * collateral_info.interest_rate >= collateral_info.dust):
    #             "do something here"
    #
    #     dink = loan.collateral_amt * dart / loan.debt_amt
    #     if not (dink > 0):
    #         return
    #     if not (dart <= 2**255 and dink <= 2**255):
    #         "do something here"

        # vat.grab(
        #     ilk, urn, milk.clip, address(vow), -int256(dink), -int256(dart)
        # );
        # // --- CDP Confiscation ---
#     function grab(bytes32 i, address u, address v, address w, int dink, int dart) external auth {
#         Urn storage urn = urns[i][u];
#         Ilk storage ilk = ilks[i];

#         urn.ink = _add(urn.ink, dink);
#         urn.art = _add(urn.art, dart);
#         ilk.Art = _add(ilk.Art, dart);

#         int dtab = _mul(ilk.rate, dart);

#         gem[i][v] = _sub(gem[i][v], dink);
#         sin[w]    = _sub(sin[w],    dtab);
#         vice      = _sub(vice,      dtab);
#     }

        # uint256 due = mul(dart, rate);
        # vow.fess(due);

        # {   // Avoid stack too deep
        #     // This calculation will overflow if dart*rate exceeds ~10^14
        #     uint256 tab = mul(due, milk.chop) / WAD;
        #     Dirt = add(Dirt, tab);
        #     ilks[ilk].dirt = add(milk.dirt, tab);

        #     id = ClipperLike(milk.clip).kick({
        #         tab: tab,
        #         lot: dink,
        #         usr: urn,
        #         kpr: kpr
        #     });
        # }

        # emit Bark(ilk, urn, dink, dart, due, milk.clip, id);
    def change_collateral_rate(self, collateral_type, u, new_rate):
        if self.bank_is_open:
            self.collateral_infos[collateral_type]
        pass

    # let me push
