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
                max_debt_amt, interest_rate):
        self.safe_spot_price = safe_spot_price
        self.total_debt_amt = total_debt_amt
        self.max_debt_amt = max_debt_amt
        self.interest_rate = interest_rate

class Bank:
    
    def __init__():
        self.loans = [][]
        self.collateral_specifications = []
        self.bank_is_open = 1
        self.total_debt_issued = 0
        self.maximum_debt_amount = 0
        self.approved_loan_modifiers = [][]

    def modifyLoan(collateral_type, delta_collateral_amount, delta_debt_amount, user, sender):
        if not self.bank_is_open: return
        
        loan = self.loans[collateral_type][user]
        collateral_specification = self.collateral_specifications[collateral_type]
        loan.collateral_amount += delta_collateral_amount
        loan.debt_amount += delta_debt_amount
        collateral_specification.total_debt_amount += delta_debt_amount
        
        dtab = delta_debt_amount * collateral_specification.interest_rate
        users_tab = collateral_specification.interest_rate * loan.debt_amount
        self.total_debt_issued = self.total_debt_issued + dtab

        debt_has_decreased = delta_debt_amount <= 0
        below_maximum_debt = self.total_debt_issued < self.maximum_debt_amount
        below_maximum_debt_per_collateral = collateral_specification.total_debt_amount * collateral_specification.interest_rate < collateral_specification.maximum_debt_amount # why interest rate
        if not (debt_has_decreased or (below_maximum_debt and below_maximum_debt_per_collateral)): return

        added_collateral = delta_collateral_amount >= 0
        added_collateral_removed_debt = delta_debt_amount <= 0 and added_collateral
        user_owes_less_than_collateral_is_worth = users_tab <= loan.collateral_amount * collateral_specification.safety_spot_price
        if not (added_collateral_removed_debt) or user_owes_less_than_collateral_is_worth: return
        approved_modifier = approved_loan_modifiers[sender][user] == 1
        if not (approved_modifier or added_collateral_removed_debt): return
        #still more to do

    def liquidate(bad_loan, collateral_type, keeper):
                if not live: return
        b_loan = bank.loans[collateral_type][bad_loan]
        collateral_spec = bank.collateral_specifications[collateral_type]
        
        pass

    pass




    // --- CDP Liquidation: all bark and no bite ---
    //
    // Liquidate a Vault and start a Dutch auction to sell its collateral for DAI.
    //
    // The third argument is the address that will receive the liquidation reward, if any.
    //
    // The entire Vault will be liquidated except when the target amount of DAI to be raised in
    // the resulting auction (debt of Vault + liquidation penalty) causes either Dirt to exceed
    // Hole or ilk.dirt to exceed ilk.hole by an economically significant amount. In that
    // case, a partial liquidation is performed to respect the global and per-ilk limits on
    // outstanding DAI target. The one exception is if the resulting auction would likely
    // have too little collateral to be interesting to Keepers (debt taken from Vault < ilk.dust),
    // in which case the function reverts. Please refer to the code and comments within if
    // more detail is desired.
    function bark(bytes32 ilk, address urn, address kpr) external returns (uint256 id) {

        (uint256 ink, uint256 art) = vat.urns(ilk, urn);
        Ilk memory milk = ilks[ilk];
        uint256 dart;
        uint256 rate;
        uint256 dust;
        {
            uint256 spot;
            (,rate, spot,, dust) = vat.ilks(ilk);
            require(spot > 0 && mul(ink, spot) < mul(art, rate), "Dog/not-unsafe");

            // Get the minimum value between:
            // 1) Remaining space in the general Hole
            // 2) Remaining space in the collateral hole
            require(Hole > Dirt && milk.hole > milk.dirt, "Dog/liquidation-limit-hit");
            uint256 room = min(Hole - Dirt, milk.hole - milk.dirt);

            // uint256.max()/(RAD*WAD) = 115,792,089,237,316
            dart = min(art, mul(room, WAD) / rate / milk.chop);

            // Partial liquidation edge case logic
            if (art > dart) {
                if (mul(art - dart, rate) < dust) {

                    // If the leftover Vault would be dusty, just liquidate it entirely.
                    // This will result in at least one of dirt_i > hole_i or Dirt > Hole becoming true.
                    // The amount of excess will be bounded above by ceiling(dust_i * chop_i / WAD).
                    // This deviation is assumed to be small compared to both hole_i and Hole, so that
                    // the extra amount of target DAI over the limits intended is not of economic concern.
                    dart = art;
                } else {

                    // In a partial liquidation, the resulting auction should also be non-dusty.
                    require(mul(dart, rate) >= dust, "Dog/dusty-auction-from-partial-liquidation");
                }
            }
        }

        uint256 dink = mul(ink, dart) / art;

        require(dink > 0, "Dog/null-auction");
        require(dart <= 2**255 && dink <= 2**255, "Dog/overflow");

        vat.grab(
            ilk, urn, milk.clip, address(vow), -int256(dink), -int256(dart)
        );

        uint256 due = mul(dart, rate);
        vow.fess(due);

        {   // Avoid stack too deep
            // This calcuation will overflow if dart*rate exceeds ~10^14
            uint256 tab = mul(due, milk.chop) / WAD;
            Dirt = add(Dirt, tab);
            ilks[ilk].dirt = add(milk.dirt, tab);

            id = ClipperLike(milk.clip).kick({
                tab: tab,
                lot: dink,
                usr: urn,
                kpr: kpr
            });
        }

        emit Bark(ilk, urn, dink, dart, due, milk.clip, id);
    }

    function digs(bytes32 ilk, uint256 rad) external auth {
        Dirt = sub(Dirt, rad);
        ilks[ilk].dirt = sub(ilks[ilk].dirt, rad);
        emit Digs(ilk, rad);
    }

    function cage() external auth {
        live = 0;
        emit Cage();
    }
}
