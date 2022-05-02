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
        self.bid_countdown = datetime.timedelta(hours=3) # 3 hours
        self.auction_expiry = datetime.timedelta(days=2) # 2 days
        self.auction_count = 0
        self.current_dai
        self.max_dai
        self.auctions = Dict[int, SurplusAuction]()
        self.auction_address
        
    
    ######### ADMIN FUNCTIONS ########

    # adjustParam
    # a function used by governance to set min_bid, bid_expiry, 
    # and auction_expiry
    def adjustParam(self, parameter_name, param_value):
        if parameter_name == 'min_bid':
            self.min_bid = param_value
        elif parameter_name == 'bid_expiry':
            self.bid_countdown = param_value
        elif parameter_name == 'auction_expiry':
            self.auction_expiry = param_value
        else:
            print('Invalid parameter name')
    
    def startSurplusAuction(self, dai_bounty, bid, bidder):
        assert(self.live == True)
        self.current_dai += dai_bounty
        assert(self.max_dai >= self.current_dai)
        self.auction_count += 1
        id = self.auction_count
        auction = SurplusAuction(mkr_bid=bid, bidder=bidder, dai_bounty=dai_bounty, bid_expiry=self.bid_countdown, auction_expiry=self.auction_expiry+datetime.datetime.now())
        self.auctions[id] = auction
        self.cdp_engine.move(bidder, dai_bounty, self.auction_address)
        print('Auction started: ' + str(id))
    
    def extendAuction(self, id):
        assert(self.auctions[id].auction_expiry < datetime.datetime.now())
        assert(self.auctions[id].bid_countdown == 0)
        self.auctions[id].auction_expiry = self.auction_expiry+datetime.datetime.now()
        

        

        


