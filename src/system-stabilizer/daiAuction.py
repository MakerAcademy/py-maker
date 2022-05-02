import datetime
from typing import Dict

# This CDP engine is just a placeholder for vat. 
# it contains move, which just tranfers tokens between addresses in wallet
class CDPEngine:
    def __init__(self):
        self.wallets = {}

    def move(self, src_address, quantity, dest_address):
        self.wallets[src_address] -= quantity
        self.wallets[dest_address] += quantity
    pass

class SurplusAuction:
    def __init__(self, mkr_bid, bidder, dai_bounty, bid_countdown, auction_countdown):
        self.mkr_bid = mkr_bid
        self.bidder = bidder
        self.dai_bounty = dai_bounty
        self.bid_countdown = bid_countdown
        self.auction_countdown = auction_countdown
    
class SurplusAuctionHouse:
    def __init__(self, cdp_engine: CDPEngine, mkr_address, auction_address, max_dai):
        self.cdp_engine = cdp_engine
        self.mkr_address = mkr_address
        self.live = True
        self.min_bid = 1.05
        self.bid_countdown = datetime.timedelta(hours=3) # 3 hours
        self.auction_expiry = datetime.timedelta(days=2) # 2 days
        self.auction_count = 0
        self.current_dai = 0
        self.max_dai = max_dai
        self.auctions = Dict[int, SurplusAuction]()
        self.auction_address = auction_address
        
    
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
    
    def bid(self, id, mkr_bid, bidder, dai_bounty):
        assert(self.live == True)
        assert(self.auctions[id].bid_expiry > datetime.datetime.now())
        assert(self.auctions[id].mkr_bid < mkr_bid)
        assert(self.auctions[id].bidder != bidder)
        self.cdp_engine.move(self.mkr_address, self.auctions[id].mkr_bid, self.auctions[id].bidder)
        self.cdp_engine.move(bidder, mkr_bid, self.mkr_address)
        self.auctions[id].mkr_bid = mkr_bid
        self.auctions[id].bidder = bidder
        self.auctions[id].dai_bounty = dai_bounty
        print('Bid placed: ' + str(id))

    def settleAuction(self, id):
        assert(self.live == 1, 'Auction is not live')
        assert(self.auctions[id].bid_countdown == 0)
        dai_bounty = self.auctions[id].dai_bounty
        self.cdp_engine.move(self.auction_address, dai_bounty, self.auctions[id].bidder)
        self.current_dai -= dai_bounty
        self.mkr_address -= self.auctions[id].mkr_bid
        del self.auctions[id]
        print('Auction settled: ' + str(id))

    def endSurplusAuction(self):
        assert(self.live == True)
        self.live = False
        print('Surplus Auction ended')

    def emergencySettle(self, id):
        assert(self.live == False)
        assert(self.auctions[id].bidder != 0)
        self.cdp_engine.move(self.mkr_address, self.auctions[id].mkr_bid, self.auctions[id].bidder)
        del self.auctions[id]
