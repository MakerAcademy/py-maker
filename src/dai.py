from typing import Dict

from src.primitives import User, Ticker


class Dai
    def __init__(self, total_supply: float,
                 balance_of: Dict[User, float],
                 allowance: Dict[User, Dict[User, float]],
                 nonces: Dict[User, float],
                 name: str = "Dai Stablecoin",
                 ticker: str = Ticker("DAI"),
                 version: float = 1):
        self.name = name
        # In dss, ticker = symbol
        self.ticker = ticker
        self.version = version
        # In dss, total_supply = totalSupply
        self.total_supply = total_supply
        # In dss, balance_of = balanceOf
        self.balance_of = balance_of
        self.allowance = allowance
        # In dss, balance_of = balanceOf
        self.nonces
        # In solidity, there is no in-built support for floats, but
        # in python, there is. Therefore, we don't have
        # decimanls = 18 field that exists in dss


    def transfer(self, sender: User, receiver: User, amount: float) -> bool:
        return self.transfer_from(sender=sender, source_account=sender,
                                 destination_account=receiver, amount=amount)

    # In dss, transfer_from is equivalent to transfer
    def transfer_from(self, sender: User, source_account: User,
                     destination_account: User, amount: float) -> bool:
        if self.balance_of[sender] < amount: return False
        if sender != source_account and self.allowance[source_account][sender] < amount: return False
        if sender != source_account and self.allowance[source_account][sender] >= amount:
            self.allowance[source_account][sender] -= amount
        self.balance_of[source_account] -= amount
        self.balance_of[destination_account] += amount
        return True

    def mint(self, beneficiary: User, amount: float):
        self.balance_of[beneficiary] += amount
        self.total_supply += amount

    def burn(self, sender: User, affected_user: User, amount: float):
        if self.balance_of[affected_user] < amount: return
        if sender != affected_user and self.allowance[affected_user][sender] < amount: return
        if sender != affected_user and self.allowance[affected_user][sender] >= amount:
            self.allowance[affected_user][sender] -= amount
        self.balance_of[affected_user] -= amount
        self.total_supply -= amount


    def approve(self, sender: User, user: User, amount: float) -> bool:
        self.allowance[sender][user] = amount
        return True


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