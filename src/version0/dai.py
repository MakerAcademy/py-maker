# This file replicates the logic of dai.sol of the makerdao/dss
# repository. dai.sol can be found here: https://github.com/makerdao/dss/blob/master/src/dai.sol
# Authored by Colby Anderson

from typing import Dict

from src.version0.primitives import User, require


# Dai represents the stablecoin that the Bank mints and gives out
# when Users take out loans. This class keeps track of who owns
# DAI, who is allowed to transfer Dai, and supports the logic
# of transferring DAI, etc.
# [dai.sol] Replicates contract Dai
class Dai:
    def __init__(self, sender: User, total_supply: float,
                 balance_of: Dict[User, float],
                 allowance: Dict[User, Dict[User, float]],
                 authorized_users: Dict[User, bool]):
        # A dictionary from users to bool, wherein [user] = True
        # if the user has authorization to access special methods
        # [dai.sol] Replicates wards
        self.authorized_users = authorized_users
        self.authorized_users[sender] = True
        # This represents the name of the class. When an object of this
        # class calls other functions in different classes, and these external
        # functions need the name of a caller, this name will be passed.
        # [dai.sol] Replicates symbol
        self.name = User("DAI")
        # The total amount of DAI in circulation (that has been minted, but not
        # burned).
        # [dai.sol] Replicates totalSupply
        self.total_supply = total_supply
        # A dictionary that maps each User to how much DAI they have
        # [dai.sol] Replicates balanceOf
        self.balance_of = balance_of
        # A dictionary that shows how much certain Users are allowed
        # to transfer (spend) for other Users.
        # User who owns DAI -> User wanting to spend their DAI -> approved
        # amount to spend
        # [dai.sol] Replicates allowance
        self.allowance = allowance

    # -------------------------------------------------------
    # ------------------- Transferring DAI ------------------
    # -------------------------------------------------------

    # This is a wrapper function around transfer_from. It will transfer
    # some amount of funds from the sender [caller of this function] to the receiver.
    # Returns True if the transfer was successful, False otherwise
    # [dai.sol] Replicates transfer(address dst, uint wad) external returns (bool)
    def transfer(self, sender: User, receiver: User, amount: float) -> bool:
        return self.transfer_from(sender=sender, source_account=sender,
                                 destination_account=receiver, amount=amount)

    # Transfers funds from the source account to the destination account if
    # the source account has enough funds to transfer, AND the source accoun is the
    # sender or has approved more than this amount of funds for the sender.
    # Returns True if the transfer was successful, False otherwise
    # [dai.sol] Replicates transferFrom(address src, address dst, uint wad) public returns (bool)
    def transfer_from(self, sender: User, source_account: User,
                     destination_account: User, amount: float) -> bool:
        require(necessary_condition=self.balance_of.get(source_account, 0) >= amount,
                error_message="Affected user doesn't have enough DAI to burn")
        if source_account != sender:
            require(necessary_condition=self.allowance.get(source_account, False) is not False,
                    error_message="Affected user hasn't approved anyone to spend for him")
            require(necessary_condition=self.allowance[source_account].get(sender, 0) >= amount,
                    error_message="Affected user hasn't approved enough transferrable funds for the sender")
            self.allowance[source_account][sender] -= amount
        self.balance_of[source_account] -= amount
        self.balance_of[destination_account] += amount
        return True

    # -------------------------------------------------------
    # -------------- Creating/Destroying DAI ----------------
    # -------------------------------------------------------

    # Mints DAI (creates DAI and gives it to) for some beneficiary
    # if the sender [caller of the function] has authorization access.
    # [dai.sol] Replicates mint(address usr, uint wad) external auth
    def mint(self, sender: User, beneficiary: User, amount: float):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.balance_of[beneficiary] += amount
        self.total_supply += amount

    # The sender will burn some amount of DAI for the affected user if
    # the affected user has enough funds to burn, AND the affected user is the
    # sender or has approved more than this amount of funds for the sender.
    # [dai.sol] Replicates burn(address usr, uint wad) external
    def burn(self, sender: User, affected_user: User, amount: float):
        require(necessary_condition=self.balance_of.get(affected_user, 0) >= amount,
                error_message="Affected user doesn't have enough DAI to burn")
        if sender != affected_user:
            require(necessary_condition=self.allowance.get(affected_user, False) is not False,
                    error_message="Affected user hasn't approved anyone to spend for him")
            require(necessary_condition=self.allowance[affected_user].get(sender, 0) >= amount,
                    error_message="Affected user hasn't approved enough transferrable funds for the sender")
            self.allowance[affected_user][sender] -= amount
        self.balance_of[affected_user] -= amount
        self.total_supply -= amount

    # -------------------------------------------------------
    # ------ Approving Others For Fund Transfers ------------
    # -------------------------------------------------------

    # The sender [caller of the function] is approving some user to transfer
    # a certain amount of the sender's funds as if they were the sender.
    # Returns True if the function ran successfully, and False otherwise.
    # [dai.sol] Replicates approve(address usr, uint wad) external returns (bool)
    def approve(self, sender: User, user: User, amount: float) -> bool:
        if self.allowance.get(sender, False) is False:
            self.allowance[sender] = {}
        self.allowance[sender][user] = amount
        return True

    # -------------------------------------------------------
    # ---------- Granting/Removing Authorization ------------
    # -------------------------------------------------------

    # Grants authorization for a specific user if the sender [caller
    # of the function] has authorization access.
    # [join.sol] Replicates rely(address guy) external auth
    def grant_authorization(self, sender: User, new_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.authorized_users[new_user] = True

    # Removes authorization for a specific user if the sender [caller
    # of the function] has authorization access.
    # [join.sol] Replicates deny(address guy) external auth
    def remove_authorization(self, sender: User, old_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.authorized_users[old_user] = False





#
#     // --- EIP712 niceties ---
#     bytes32 public DOMAIN_SEPARATOR;
#     // bytes32 public constant PERMIT_TYPEHASH = keccak256("Permit(address holder,address spender,uint256 nonce,uint256 expiry,bool allowed)");
#     bytes32 public constant PERMIT_TYPEHASH = 0xea2aa0a1be11a07ed86d755c93467f4f82362b452371d1ba94d1715123511acb;
#
#     constructor(uint256 chainId_) public {
#         wards[msg.sender] = 1;
#         DOMAIN_SEPARATOR = keccak256(abi.encode(
#             keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
#             keccak256(bytes(name)),
#             keccak256(bytes(version)),
#             chainId_,
#             address(this)
#         ));
#     }
#
#     // --- Alias ---
#     function push(address usr, uint wad) external {
#         transferFrom(msg.sender, usr, wad);
#     }
#     function pull(address usr, uint wad) external {
#         transferFrom(usr, msg.sender, wad);
#     }
#     function move(address src, address dst, uint wad) external {
#         transferFrom(src, dst, wad);
#     }
#
#     // --- Approve by signature ---
#     function permit(address holder, address spender, uint256 nonce, uint256 expiry,
#                     bool allowed, uint8 v, bytes32 r, bytes32 s) external
#     {
#         bytes32 digest =
#             keccak256(abi.encodePacked(
#                 "\x19\x01",
#                 DOMAIN_SEPARATOR,
#                 keccak256(abi.encode(PERMIT_TYPEHASH,
#                                      holder,
#                                      spender,
#                                      nonce,
#                                      expiry,
#                                      allowed))
#         ));
#
#         require(holder != address(0), "Dai/invalid-address-0");
#         require(holder == ecrecover(digest, v, r, s), "Dai/invalid-permit");
#         require(expiry == 0 || now <= expiry, "Dai/permit-expired");
#         require(nonce == nonces[holder]++, "Dai/invalid-nonce");
#         uint wad = allowed ? uint(-1) : 0;
#         allowance[holder][spender] = wad;
#         emit Approval(holder, spender, wad);
#     }
# }