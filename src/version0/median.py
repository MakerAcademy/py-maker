from typing import Dict, List

from src.version0.primitives import Ticker, Contract, Signature, ec_recover, compute_message


class Median:

    def __init__(self, price: float, time_of_last_update: float,
                 authorized_price_queriers: Dict[Contract, bool],
                 authorized_contracts_to_read_values: Dict[Contract, bool],
                 type_of_asset: Ticker = "ETH", valid_message_threshold: int = 1):
        # In dss, price = val
        self.price = price
        # In dss, time_of_last_update = age
        self.time_of_last_update = time_of_last_update
        # In dss, type_of_asset = wat
        self.type_of_asset =  type_of_asset
        # In dss, valid_message_threshold = bar
        self.valid_message_threshold = valid_message_threshold
        # In dss, authorized_price_queriers = orcl
        self.authorized_price_queriers = authorized_price_queriers
        # In dss, authorized_contracts_to_read_values = bud
        self.authorized_contracts_to_read_values = authorized_contracts_to_read_values
        # In dss,
        self.slot = 0

    def read(self, sender):
        if self.price <= 0 or not self.authorized_contracts_to_read_values[sender]: return
        return self.price

    def peek(self, sender) -> (float, bool):
        if not self.authorized_contracts_to_read_values[sender]: return
        return self.price, self.price > 0

    def recover(self):
        pass


    // Mapping for at most 256 oracles
    mapping (uint8 => address) public slot;

    modifier toll { require(bud[msg.sender] == 1, "Median/contract-not-whitelisted"); _;}

    def recover(self, value: float, age: float, signature: Signature):
        return ec_recover(compute_message(value, age), signature)

    def poke(self, values: List[float], ages: List[float], signatures: List[Signature]):
        if val.length != bar: return

        bloom = 0
        last = 0

        for i in range(0, len(values)):
            signer = self.recover(values[i], ages[i], signatures[i])
            if not self.authorized_price_queriers[signer]: return
            if ages[i] <= self.time_of_last_update: return
            if values[i] < last: return
            last = values[i]




        val = uint128(val_[val_.length >> 1]);
        age = uint32(block.timestamp);

        emit LogMedianPrice(val, age);
    }

    function lift(address[] calldata a) external note auth {
        for (uint i = 0; i < a.length; i++) {
            require(a[i] != address(0), "Median/no-oracle-0");
            uint8 s = uint8(uint256(a[i]) >> 152);
            require(slot[s] == address(0), "Median/signer-already-exists");
            orcl[a[i]] = 1;
            slot[s] = a[i];
        }
    }

    function drop(address[] calldata a) external note auth {
       for (uint i = 0; i < a.length; i++) {
            orcl[a[i]] = 0;
            slot[uint8(uint256(a[i]) >> 152)] = address(0);
       }
    }

    function setBar(uint256 bar_) external note auth {
        require(bar_ > 0, "Median/quorum-is-zero");
        require(bar_ % 2 != 0, "Median/quorum-not-odd-number");
        bar = bar_;
    }

    function kiss(address a) external note auth {
        require(a != address(0), "Median/no-contract-0");
        bud[a] = 1;
    }

    function diss(address a) external note auth {
        bud[a] = 0;
    }

    function kiss(address[] calldata a) external note auth {
        for(uint i = 0; i < a.length; i++) {
            require(a[i] != address(0), "Median/no-contract-0");
            bud[a[i]] = 1;
        }
    }

    function diss(address[] calldata a) external note auth {
        for(uint i = 0; i < a.length; i++) {
            bud[a[i]] = 0;
        }
    }
}