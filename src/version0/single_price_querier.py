# This file replicates the logic of osm.sol of the makerdao/osm
# repository. osm.sol can be found here: https://github.com/makerdao/osm/blob/master/src/osm.sol
# Authored by Colby Anderson

from typing import Dict
from primitives import require, User, get_current_blocktime


# Represents a wrapper around a price from a feed. Also
# stores whether the current price is available or not.
# [osm.sol] Replicates Feed
class Feed:
    def __init__(self, spot_price: float, feed_is_live: bool):
        # The spot price queried from some feed source.
        # [osm.sol] Replicates val
        self.spot_price = spot_price
        # Whether the spot price was actually able to
        # be queried or not
        # [osm.sol] Replicates has
        self.feed_is_live = feed_is_live


# This class is responsible for interfacing with a price
# feed for one collateral type. It stores the current price
# and the next price. After a certain time delay, these values
# can be updated.
# [osm.sol] Replicates contract OSM is LibNote
class SingleCollateralPriceQuerier:
    def __init__(self, sender: User, update_mechanism_running: bool,
                 feed_source: User, last_update_time: float,
                 current_feed: Feed, next_feed: Feed,
                 can_access_feeds: Dict[User, bool],
                 authorized_users: Dict[User, bool],
                 update_feed_delay: float = 3600):
        # True when the mechanism is paused (means an update is about to
        # happen) and False otherwise.
        # [osm.sol] Replicates stopped
        self.update_mechanism_running = update_mechanism_running
        # The User that this contract queries for the next price feed
        # [osm.sol] Replicates src
        self.feed_source = feed_source
        # The time in seconds before the next update to the price feed
        # can be enacted.
        # Defaults to 3600 (amount of seconds in an hour)
        # [osm.sol] Replicates hop
        self.update_feed_delay = update_feed_delay
        # The time [in seconds from Unix epoch] when the last
        # update to the price feed (current price is next) occurred
        # [osm.sol] Replicates zzz
        self.last_update_time = last_update_time
        # A Feed object that represents the current feed price
        # [osm.sol] Replicates cur
        self.current_feed = current_feed
        # A Feed object that represents the next feed price
        # [osm.sol] Replicates nxt
        self.next_feed = next_feed
        # A dictionary from users to bool, wherein [user] = True
        # if the user has read access to the price feed information
        # [osm.sol] Replicates bud
        self.can_access_feeds = can_access_feeds
        # A dictionary from users to bool, wherein [user] = True
        # if the user has authorization to access special methods
        # [osm.sol] Replicates wards
        self.authorized_users = authorized_users
        self.authorized_users[sender] = True
        # This represents the name of the class. When an object of this
        # class calls other functions in different classes, and these external
        # functions need the name of a caller, this name will be passed.
        self.name = User("SingleCollateralPriceQuerier")

    # -------------------------------------------------------
    # ---------------- Updating The Price Feed --------------
    # -------------------------------------------------------

    # Updates the current feed to the next feed and queries the feed
    # source for the next feed. This can only occur if the update mechanism
    # is currently paused and if an update can actually occur.
    # [osm.sol] Replicates poke() external note stoppable
    # TODO: Rename peek once feed source contract is consolidated
    def update_spot_price(self):
        require(necessary_condition=self.update_mechanism_running is False,
                error_message="The update mechanism must be paused beforehand")
        require(necessary_condition=self.update_can_occur() is True,
                error_message="An update can not yet occur due to the time delay between updates")
        price, ok = self.feed_source.peek()
        if ok:
            self.current_feed = self.next_feed
            self.next_feed = Feed(spot_price=price, feed_is_live=True)
            self.last_update_time = self.time_of_previous_update(
                current_timestamp=get_current_blocktime())

    # -------------------------------------------------------
    # -- Reading Information About Times Of Feed Updates ----
    # -------------------------------------------------------

    # Returns the time (in seconds from Unix epoch) that the previous update to
    # the price feed occurred. This is calculated by 1) determining the remainder
    # of the current time divided by the time delay in updating. The remainder will
    # tell you how many seconds from the last update. 2) subtracting the remainder
    # (seconds from last update) from the current time will give you the time
    # of the previous update.
    # [osm.sol] Replicates prev(uint ts) internal view returns (uint64)
    def time_of_previous_update(self, current_timestamp: float) -> float:
        require(necessary_condition=self.update_feed_delay != 0,
                error_message="The time delay in updating the price feed has not been set")
        return current_timestamp - (current_timestamp % self.update_feed_delay)

    # Returns True if an update to the price feed can occur, and false
    # otherwise. True/False is calculated by determining whether the
    # current time is ahead of the time of the last update + the time delay
    # in updating the feed.
    # [osm.sol] Replicates pass() public view returns (bool ok)
    def update_can_occur(self) -> bool:
        return get_current_blocktime() >= self.update_feed_delay + self.last_update_time

    # -------------------------------------------------------
    # --------------- Reading The Price Feed ----------------
    # -------------------------------------------------------

    # Returns the current price feed if the sender [caller of the function] has
    # read access.
    # [osm.sol] Replicates peek() external view toll returns (bytes32,bool)
    def get_current_feed(self, sender: User) -> Feed:
        require(necessary_condition=self.can_access_feeds.get(sender, False) is True,
                error_message="Sender doesn't have read access")
        return self.current_feed

    # Returns the next price feed if the sender [caller of the function] has
    # read access.
    # [osm.sol] Replicates peep() external view toll returns (bytes32,bool)
    def get_next_feed(self, sender: User) -> Feed:
        require(necessary_condition=self.can_access_feeds.get(sender, False) is True,
                error_message="Sender doesn't have read access")
        return self.next_feed

    # Returns the price of the current price feed if the sender [caller
    # of the function] has read access and the current price feed is
    # live (currently turned on).
    # [osm.sol] Replicates read() external view toll returns (bytes32)
    def get_current_feed_price(self, sender: User) -> float:
        require(necessary_condition=self.can_access_feeds.get(sender, False) is True,
                error_message="Sender doesn't have read access")
        require(necessary_condition=self.current_feed.feed_is_live is True,
                error_message="Current price feed is not live [not turned on]")
        return self.current_feed.spot_price

    # -------------------------------------------------------
    # --------- Updating Aspects Of The Price Feed ----------
    # -------------------------------------------------------

    # Changes the delay in updating the price from the feed if the
    # sender [caller of the function] has authorization and the new
    # time delay is above zero.
    # [osm.sol] Replicates step(uint16 ts) external auth
    def change_update_feed_delay(self, sender: User, update_feed_delay: float):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        require(necessary_condition=update_feed_delay > 0,
                error_message="The delay in updating the price from a feed must be above zero")
        self.update_feed_delay = update_feed_delay

    # Changes the source of the price feed (we will get the price updates
    # from a different user) if the sender [caller of the function] has authorization.
    # [osm.sol] Replicates change(address src_) external note auth
    def change_feed_source(self, sender: User, new_feed_source: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.feed_source = new_feed_source

    # -------------------------------------------------------
    # ----- Configuring Read Access To The Price Feed -------
    # -------------------------------------------------------

    # Grants read access to the price feed for a particular new user if
    # the sender [caller of the function] has authorization.
    # [osm.sol] Replicates kiss(address a) external note auth
    def grant_access_to_feed(self, sender: User, new_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.can_access_feeds[new_user] = True

    # Removes read access to the price feed for a particular old user if
    # the sender [caller of the function] has authorization.
    # [osm.sol] Replicates diss(address a) external note auth
    def remove_access_to_feed(self, sender: User, old_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.can_access_feeds[old_user] = False

    # -------------------------------------------------------
    # ------- Starting/Stopping The Update Mechanism --------
    # -------------------------------------------------------

    # Pauses the update mechanism if the sender [caller of the function]
    # has authorization.
    # [osm.sol] Replicates stop() external note auth
    def pause(self, sender: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.update_mechanism_running = False

    # Resumes the update mechanism if the sender [caller of the function]
    # has authorization.
    # [osm.sol] Replicates start() external note auth
    def resume(self, sender: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.update_mechanism_running = True

    # Pauses the update mechanism and removes the current price feed information
    # if the sender [caller of the function] has authorization.
    # [osm.sol] Replicates void() external note auth
    def stop_and_make_void_feeds(self, sender: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.current_feed = Feed(spot_price=0, feed_is_live=False)
        self.update_mechanism_running = False

    # -------------------------------------------------------
    # ---------- Granting/Removing Authorization ------------
    # -------------------------------------------------------

    # Grants authorization for a specific user if the sender [caller
    # of the function] has authorization access.
    # [osm.sol] Replicates rely(address guy) external auth
    def grant_authorization(self, sender: User, new_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.authorized_users[new_user] = True

    # Removes authorization for a specific user if the sender [caller
    # of the function] has authorization access.
    # [osm.sol] Replicates deny(address guy) external auth
    def remove_authorization(self, sender: User, old_user: User):
        require(necessary_condition=self.authorized_users.get(sender, False) is True,
                error_message="Sender doesn't have authorized access")
        self.authorized_users[old_user] = False
