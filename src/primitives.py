# User just represents the name of a user
# In dss, contract = address (kind of)
class Contract:
    def __init__(self, name: str):
        self.name = name

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