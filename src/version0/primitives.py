# This file doesn't have an equivalent file in the dss. This file
# just contains a list of common functions and data structures
# that solidity usually has as an automatic feature of the language,
# whereas python does not.
# Authored Colby Anderson

import time


# Represents a ticker for an asset, i.e. "ETH"
# or "USD", etc.
# [dss] Replicates bytes32 (for the most part)
class Ticker:
    def __init__(self, tick: str):
        self.tick = tick


# Represents the caller of a function, which
# could be simulated by a person with an account
# on the blockchain or a contract that exists on the
# blockchain
# [dss] Replicates address
class User:
    def __init__(self, name: str):
        self.name = name


# Raises an exception if the necessary condition is false.
# This loosely replaces the inbuilt "require" function from
# solidity.
# [solidity] Replicates require
def require(necessary_condition: bool, error_message: str):
    if not necessary_condition:
        raise Exception(error_message)


# Gets the current time (in seconds from Unix epoch).
# [solidity] Replicates block.timestamp
def get_current_blocktime() -> float:
    return time.time()


# class SignedMessage:
#     def __init__(self):
#         pass
#
#
# class Signature:
#     def __init__(self):
#         pass
#
#
# def ec_recover():
#     pass
#
#
# def compute_message():
#     pass
