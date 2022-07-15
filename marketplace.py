import smartpy as sp

class marketplace(sp.Contract):
    def __init__(self,admin, metadata, royaltyPercentage, token):
        self.init(
            token = token,
            metadata = metadata,
            admin = admin,
            royaltyPercentage=royaltyPercentage,
            listings= sp.map(listingId=sp.TNat, tvalue=sp.TRecord(amount=sp.TNat, tokenId=sp.TNat, seller=sp.TAddress, price_per_unit=sp.TMutez, active=sp.bool)),
            auctions= sp.map(auctionId=sp.TNat, tvalue=sp.Trecord(amount=sp.Tnat, tokenId=sp.TNat, seller=sp.TAddress, timePeriod=sp.timestamp)),
            
        )