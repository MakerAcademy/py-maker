import time

from typing import Dict
from primitives import Contract

# In dss, equivalent to constant value within OSM
# contract, uint16  constant ONE_HOUR = uint16(3600);
ONE_HOUR = 3600

# In dss, Feed = Feed
class Feed:
    def __init__(self, spot_price: float, feed_is_live: bool):
        # In dss, spot_price = val
        self.spot_price = spot_price
        # In dss, feed_is_live = has
        self.feed_is_live = feed_is_live

class SingleCollateralPriceQuerier:
    def __init__(self, price_feed_is_enabled: bool,
                 feed_source: Contract,
                 last_update_time: float,
                 current_feed: Feed,
                 next_feed: Feed,
                 can_access_feeds: Dict[Contract, bool],
                 update_feed_delay: float = ONE_HOUR):
        # In dss, price_feed_is_enabled = stopped
        self.price_feed_is_enabled = price_feed_is_enabled
        # In dss, feed_source = src
        self.feed_source = feed_source
        # In dss, update_feed_delay = hop
        self.update_feed_delay = update_feed_delay
        # In dss, last_update_time = zzz
        self.last_update_time = last_update_time
        # In dss, current_feed = cur
        self.current_feed = current_feed
        # In dss, next_feed = nxt
        self.next_feed = next_feed
        # In dss, can_access_feeds = bud
        self.can_access_feeds = can_access_feeds

    # In dss, disable_price_feed is equivalent to the function stop
    # function stop() external note auth {
    #         stopped = 1;
    #     }
    def disable_price_feed(self):
        self.price_feed_is_enabled = False

    # In dss, enable_price_feed is equivalent to the function start
    # function start() external note auth {
    #         stopped = 0;
    #     }
    def enable_price_feed(self):
        self.price_feed_is_enabled = True

    # In dss, change_feed is equivalent to the function change
    # function change(address src_) external note auth {
    #         src = src_;
    #     }
    def change_feed_source(self, new_feed_source: Contract):
        self.feed_source = new_feed_source

    # In dss, get_current_blocktime is equivalent to the function era
    # function era() internal view returns (uint) {
    #         return block.timestamp;
    #     }
    def get_current_blocktime(self) -> float:
        return time.time()

    # function prev(uint ts) internal view returns (uint64) {
    #         require(hop != 0, "OSM/hop-is-zero");
    #         return uint64(ts - (ts % hop));
    #     }
    def time_of_previous_update(self, current_timestamp: float):
        if (self.update_feed_delay == 0): return 0
        return current_timestamp - (current_timestamp % self.update_feed_delay)

    modifier toll { require(bud[msg.sender] == 1, "OSM/contract-not-whitelisted"); _; }

    # function step(uint16 ts) external auth {
    #         require(ts > 0, "OSM/ts-is-zero");
    #         hop = ts;
    #     }
    def change_update_feed_delay(self, new_interval):
        if new_interval <= 0: return
        self.update_feed_delay = new_interval

    #     function void() external note auth {
    #         cur = nxt = Feed(0, 0);
    #         stopped = 1;
    #     }
    def stop_and_make_void_feeds(self):
        self.current_feed = Feed(spot_price=0, feed_is_live=False)
        self.price_feed_is_enabled = False

    #     function pass() public view returns (bool ok) {
    #         return era() >= add(zzz, hop);
    #     }
    def update_can_occur(self):
        return self.get_current_blocktime() >= self.update_feed_delay + self.last_update_time

    # In dss, this function is equivalent to poke
    def update_spot_price(self):
        if not self.update_can_occur(): return
        price, ok = self.feed_source.peek()
        if ok:
            self.current_feed = self.next_feed
            self.next_feed = Feed(price, True)
            self.last_update_time = self.time_of_previous_update(self.get_current_blocktime())

    #     function peek() external view toll returns (bytes32,bool) {
    #         return (bytes32(uint(cur.val)), cur.has == 1);
    #     }
    def get_current_feed(self, sender):
        if self.can_access_feeds[sender] is False: return
        return self.current_feed.spot_price, self.current_feed.feed_is_live

    #     function peep() external view toll returns (bytes32,bool) {
    #         return (bytes32(uint(nxt.val)), nxt.has == 1);
    #     }
    def get_next_feed(self, sender):
        if self.can_access_feeds[sender] is False: return
        return self.next_feed.spot_price, self.next_feed.feed_is_live

    #     function read() external view toll returns (bytes32) {
    #         require(cur.has == 1, "OSM/no-current-value");
    #         return (bytes32(uint(cur.val)));
    #     }
    def get_current_feed_price(self, sender):
        if self.can_access_feeds[sender] is False: return
        if self.current_feed.feed_is_live is False: return
        return self.current_feed.spot_price

    #     function kiss(address a) external note auth {
    #         require(a != address(0), "OSM/no-contract-0");
    #         bud[a] = 1;
    #     }
    def grant_access_to_feed(self, contract: Contract):
        self.can_access_feeds[contract] = True

    # function diss(address a) external note auth {
    #     bud[a] = 0;
    # }
    def remove_access_to_feed(self, contract: Contract):
        self.can_access_feeds[contract] = False