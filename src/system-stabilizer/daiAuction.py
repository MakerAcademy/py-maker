import datetime
from typing import Dict


class SurplusAuction:
    def __init__(self, mkr_bid, bidder, dai_bounty, bid_expiry, auction_expiry):
        self.mkr_bid = mkr_bid
        self.bidder = bidder
        self.dai_bounty = dai_bounty
        self.bid_expiry = bid_expiry
        self.auction_expiry = auction_expiry


class SurplusAuctionHouse:
    def __init__(self, cdp_engine, mkr_address):
        self.cdp_engine = cdp_engine
        self.mkr_address = mkr_address
        self.live = True
        self.min_bid = 1.05
        self.bid_countdown = datetime.timedelta(hours=3)  # 3 hours
        self.auction_expiry = datetime.timedelta(days=2)  # 2 days
        self.auction_count = 0
        self.current_dai = float
        self.max_dai = float
        self.auctions = Dict[int, SurplusAuction]()
        self.auction_address = int

    ######### ADMIN FUNCTIONS ########
    # adjustParam
    # a function used by governance to set min_bid, bid_expiry, 
    # and auction_expiry
    def adjust_param(self, parameter_name, param_value):
        if parameter_name == 'min_bid':
            self.min_bid = param_value
        elif parameter_name == 'bid_expiry':
            self.bid_countdown = param_value
        elif parameter_name == 'auction_expiry':
            self.auction_expiry = param_value
        else:
            print('Invalid parameter name')
    
    def start_surplus_auction(self, dai_bounty, bid, bidder):
        assert self.live
        self.current_dai += dai_bounty
        assert(self.max_dai >= self.current_dai)
        self.auction_count += 1
        auction_id = self.auction_count
        auction = SurplusAuction(bid, bidder, dai_bounty, self.bid_countdown,
                                 self.auction_expiry+datetime.datetime.now())
        self.auctions[auction_id] = auction
        self.cdp_engine.move(bidder, dai_bounty, self.auction_address)
        print('Auction started: ' + str(auction_id))
    
    def extend_auction(self, auction_id):
        assert(self.auctions[auction_id].auction_expiry < datetime.datetime.now())
        assert(self.auctions[auction_id].bid_countdown == 0)
        self.auctions[auction_id].auction_expiry = self.auction_expiry+datetime.datetime.now()
