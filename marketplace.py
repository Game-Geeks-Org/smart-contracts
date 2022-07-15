import smartpy as sp

class marketplace(sp.Contract):
    def __init__(self,admin, metadata, royaltyPercentage):
        self.init(
            metadata = metadata,
            admin = admin,
            royaltyPercentage=royaltyPercentage,
            listings= sp.map(listingId=sp.TNat, tvalue=sp.TRecord(amount=sp.TNat, token=sp.TAddress, tokenId=sp.TNat, seller=sp.TAddress, price_per_unit=sp.TMutez, active=sp.bool)),
            auctions= sp.map(auctionId=sp.TNat, tvalue=sp.Trecord(amount=sp.Tnat, token=sp.TAddress, tokenId=sp.TNat, seller=sp.TAddress, timePeriod=sp.timestamp)),    
        )