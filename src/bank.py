WAD = 10 ** 18

class Loan:
    # When a user creates a loan, they will put up a certain
    # amount of collateral (collateral_amt), and then take money
    # from the bank (debt_amt). These loans will always be
    # overcollateralized: the collateral_amt should always be
    # more than the debt_amt.
    def __init__(collateral_amt, debt_amt):
        self.collateral_amt = collateral_amt
        self.debt_amt = debt_amt

class CollateralInfo:
    # CollateralInfo will keep track of different metrics about a
    # a certain collateral type. For example, the spot price of the
    # collateral (with a safety margin), the total debt (in loans)
    # that has been taken out against this particular collateral type,
    # the maximum debt that can be taken out against this particular
    # collateral type, and the interest rate for taking loans out
    # on this particular collateral type.
    def __init__(safe_spot_price, total_debt_amt,
                max_debt_amt, min_debt_amt, interest_rate):
        self.safe_spot_price = safe_spot_price
        self.total_debt_amt = total_debt_amt
        self.max_debt_amt = max_debt_amt
        self.min_debt_amt = min_debt_amt
        self.interest_rate = interest_rate
        self.max_active_aution_debt = 0
        self.amt_active_aution_debt = 0
        self.liquidation_penalty = 0

class Bank:
    
    def __init__(loans, collateral_infos, bank_is_closed, total_debt_issued,
                max_debt_amount, approved_loan_modifiers, who_owns_collateral,
                who_owns_debt):
        self.loans = loans
        self.collateral_infos = collateral_infos
        self.bank_is_closed = bank_is_closed
        self.total_debt_issued = total_debt_issued
        self.max_debt_amount = max_debt_amount
        self.approved_loan_modifiers = approved_loan_modifiers
        self.who_owns_collateral = who_owns_collateral
        self.who_owns_debt = who_owns_debt

        self.max_active_aution_debt = 0
        self.amt_active_aution_debt = 0

    def debt_has_increased(delta_debt_amt):
        return delta_debt_amt > 0

    def above_max_debt(delta_debt_amt, collateral_info):
        above_max_debt_per_collateral = (collateral_info.total_debt_amt + delta_debt_amt) * collateral_info.interest_rate > collateral_info.max_debt_amt
        above_max_system_debt = self.total_debt_issued + (delta_debt_amt * collateral_info.interest_rate) < self.max_debt_amt
        return above_max_debt_per_collateral or above_max_system_debt

    def unacceptable_loan(delta_debt_amt, delta_collateral_amt, collateral_info, loan):
        removed_collateral_added_debt = delta_collateral_amt > 0 and delta_debt_amt < 0
        users_tab = (loan.debt_amt + delta_debt_amt) * collateral_info.interest_rate
        user_took_out_too_much = users_tab >= (loan.collateral_amt + delta_collateral_amt) * collateral_info.safe_spot_price
        return removed_collateral_added_debt and user_took_out_too_much

    def sender_being_malicious(sender, user, delta_debt_amt, delta_collateral_amt):
        unapproved_modifier = self.approved_loan_modifiers[sender][user] == 1
        removed_collateral_added_debt = delta_debt_amt >= 0 and delta_collateral_amt <= 0
        return unapproved_modifier and removed_collateral_added_debt

    def miniscule_loan(loan, delta_debt_amt, collateral_info):
        new_debt_amt = loan.debt_amt + delta_debt_amt
        return new_debt_amt != 0 and new_debt_amt * collateral_info.interest_rate <= collateral_info.min_debt_amt 

    def sender_no_consent():
        return delta_collateral_amt <= 0 and not self.approved_loan_modifiers[sender][user]

    def loan_user_no_consent():
        return delta_debt_amt <= 0 and not self.approved_loan_modifiers[sender][sender]

    def unacceptable_modification(delta_debt_amt, delta_collateral_amt, collateral_info, loan, sender, user):
        debt_amt_is_unsafe = debt_has_increased(delta_debt_amt) and above_max_debt(delta_debt_amt, collateral_info)
        user_has_unacceptable_loan = unacceptable_loan(delta_debt_amt, delta_collateral_amt, collateral_info, loan)
        sender_is_malicious = sender_being_malicious(sender, user, delta_debt_amt, delta_collateral_amt)
        sender_doesnt_consent = sender_no_consent()
        loan_user_doesnt_consent = loan_user_no_consent()
        loan_isnt_miniscule = miniscule_loan(loan, delta_debt_amt, collateral_info)
        return debt_amt_is_unsafe or sender_is_malicious or user_has_unacceptable_loan
                or sender_doesnt_consent or loan_user_doesnt_consent or loan_isnt_miniscule
                or self.bank_is_closed

    def modifyLoan(collateral_type, delta_collateral_amt, delta_debt_amt, user, sender):
        collateral_info = self.collateral_infos[collateral_type]
        loan = self.loans[collateral_type][user]

        if unacceptable_modification(delta_debt_amt, delta_collateral_amt, collateral_info, loan, sender, user): return

        loan.collateral_amt += delta_collateral_amt
        loan.debt_amt += delta_debt_amt
        collateral_info.total_debt_amt += delta_debt_amt
        self.who_owns_collateral = self.who_owns_collateral[collateral_type][sender] - delta_collateral_amt
        self.who_owns_debt = self.who_owns_debt[user] + (collateral_info.interest_rate * delta_debt_amt)

    #
    #
    #
    #
    #

    def loan_is_acceptable(collateral_info, loan):
        collateral_is_worthless = collateral_info.safe_spot_price < 0
        loan_is_collateralized = loan.collateral_amt * collateral_info.safe_spot_price > loan.debt_amt * collateral_info.interest_rate)
        return collateral_is_worthless or loan_is_collateralized

    def too_much_auction_debt():
        a = self.max_active_aution_debt < self.amt_active_aution_debt
        b = collateral_info.max_active_aution_debt < collateral_info.amt_active_aution_debt
        return a or b

    def inappropriate_time_to_liquidate(collateral_info, loan):
        loan_is_safe = loan_is_acceptable(collateral_info, loan)
        too_much_debt_in_auctions = too_much_auction_debt()
        return loan_is_safe or too_much_debt_in_auctions or self.bank_is_closed

    def liquidate(collateral_type, user):
        loan = self.loans[collateral_type][user]
        collateral_info = self.collateral_infos[collateral_type]

        if inappropriate_time_to_liquidate(collateral_info, loan): return

        max_amt_to_liquidate = min(self.max_active_aution_debt - self.amt_active_aution_debt, collateral_info.max_active_aution_debt - collateral_info.amt_active_aution_debt)
        # ??????? below
        dart = min(loan.debt_amt, max_amt_to_liquidate * WAD / collateral_info.interest_rate / collateral_info.liquidation_penalty)

        if (loan.debt_amt > dart) {
            if (loan.debt_amt - dart) * collateral_info.interest_rate < collateral_info.dust {
                dart = loan.debt_amt
            } else {
                if not (dart * collateral_info.interest_rate >= collateral_info.dust)
            }
        }

        dink = loan.collateral_amt * dart / loan.debt_amt
        if not (dink > 0): return
        if not (dart <= 2**255 and dink <= 2**255)



        # vat.grab(
        #     ilk, urn, milk.clip, address(vow), -int256(dink), -int256(dart)
        # );

        # uint256 due = mul(dart, rate);
        # vow.fess(due);

        # {   // Avoid stack too deep
        #     // This calcuation will overflow if dart*rate exceeds ~10^14
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
        pass