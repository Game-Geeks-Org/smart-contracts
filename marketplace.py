import smartpy as sp

class Error_message :
    def adminOnly(self):
        return  "ADMIN_ONLY"
    
    def invalidRoyalty(self):
        return "INVALID_ROYALTY"

    def invalidTimePeriod(self):
        return "INVALID_TIME_PERIOD"

    def invalidPrice(self):
        return "INVALID_PRICE"

    def invalidAuction(self):
        return "INVALID_AUCTION"

    def invalidBid(self):
        return "INVALID_BID"

    def ownerOnly(self):
        return "OWNER_ONLY"

    def onlyWhitelisted(self):
        return "WHITELISTED_TOKENS_ONLY"

'''
    NOTE: 
    1. Royalty percentage is calculated as follows:
        - if royalty is set as 10, this means royalty is 1%
        - to calculate the royalty amount, multiply the amount involved with royalty amount then divide by 1000
        - ie.    royaltyAmount = (amountInvolved * royalty)/1000
    2. Division of royalty between third party nfts and admin is also carried in the same way as described above
'''
class marketplace(sp.Contract):
    def __init__(self,admin, _royalty):
        self.error = Error_message()
        
        #defining contract storages

        self.init_type(sp.TRecord(
         metadata= sp.TBigMap(sp.TString,sp.TBytes),
        
         ))

        #initialising contract storage
        self.init(
            metadata =sp.TBigMap(sp.TString, sp.TBytes),
            listingId = sp.nat(0),
            auctionId = sp.nat(0),
            admin = admin,
            royalty = _royalty,
            royaltyDivision = sp.big_map(tkey = sp.TAddress, tvalue = sp.TRecord(
                toAdmin = sp.TNat, toThirdParty = sp.TNat, thirdPartyAdmin = sp.TAddress
            )),
            listings= sp.map(tkey = sp.TNat, tvalue = sp.TRecord(
                token = sp.TAddress, tokenId = sp.TNat, amount = sp.TNat,
                seller = sp.TAddress, price_per_unit = sp.TMutez
            )),
            auctions = sp.map(tkey = sp.TNat, tvalue = sp.TRecord(
                token = sp.TAddress, tokenId = sp.TNat, amount = sp.TNat,
                basePrice = sp.TMutez, seller = sp.TAddress, timePeriod = sp.TTimestamp
            )),
            bids = sp.map(tkey = sp.TNat, tvalue = sp.TRecord(
                value = sp.TMutez, owner = sp.TAddress
            )),
            whitelist = sp.big_map(tkey = sp.TAddress, tvalue = sp.TBool)
        )

    # Utility Functions
    def _onlyAdmin(self):
        sp.verify(sp.sender == self.data.admin, self.error.adminOnly())

    def _checkValidRoyalty(self, amount):
        sp.verify(amount <= sp.nat(1000),self.error.invalidRoyalty())

    def _transferTokens(self,token, tokenId, amount, from_, to_):
        c = sp.contract(
                sp.TList(
                    sp.TRecord(
                        from_=sp.TAddress, 
                        txs=sp.TList(
                            sp.TRecord(
                                amount=sp.TNat, 
                                to_=sp.TAddress, 
                                token_id=sp.TNat).layout(("to_", ("token_id", "amount"))
                            )
                        )
                    )
                ), 
                token, 
                entry_point='transfer'
            ).open_some()
        sp.transfer(
            sp.list([sp.record(from_=from_, txs=sp.list([sp.record(amount=amount, to_=to_, token_id=tokenId)]))]), 
            sp.mutez(0), 
            c
        )

    def _transferRoyalty(self, toUs, toTP, tpAdmin):
        sp.send(
            tpAdmin, 
            sp.utils.nat_to_mutez(toTP)
        )
        sp.send(
            self.data.admin,
            sp.utils.nat_to_mutez(toUs)
        )

    def _refundBid(self, _auctionId):
        amount = sp.local('amount',sp.map({},tkey = sp.TNat, tvalue = sp.TMutez))
        to = sp.local('to', sp.map({},tkey = sp.TNat, tvalue = sp.TAddress))

        sp.if self.data.bids.contains(_auctionId):
            amount.value[0] = self.data.bids[_auctionId].value
            to.value[0] = self.data.bids[_auctionId].owner
            del self.data.bids[_auctionId]

        sp.if amount.value.contains(0):
            sp.send(to.value[0], amount.value[0])

    def _auctionExists(self, _auctionId):
        sp.verify(self.data.auctions.contains(_auctionId), self.error.invalidAuction())
    
    def _isBidValid(self, _auctionid):
        sp.verify(~(sp.sender == self.data.auctions[_auctionid].seller),self.error.invalidBid())
        sp.if self.data.bids.contains(_auctionid):
            sp.verify(sp.amount > self.data.bids[_auctionid].value, self.error.invalidBid())
        sp.else:
            sp.verify(sp.amount >= self.data.auctions[_auctionid].basePrice, self.error.invalidBid())

    def _updateBidder(self, _auctionId):
        self._refundBid(_auctionId)
        self.data.bids[_auctionId] = sp.record(
            value = sp.amount, owner = sp.source
        )

    def _ownerOnly(self, add1, add2):
        sp.verify(add1 == add2, self.error.ownerOnly())

    def _isWhitelisted(self, add):
        sp.verify(self.data.whitelist.contains(add),self.error.onlyWhitelisted())

    @sp.private_lambda(with_storage = 'read-write')
    def _isAuctionActive(self, _auctionId):
        sp.result(self.data.auctions[_auctionId].timePeriod > sp.now)

    @sp.private_lambda(with_storage = 'read-write')
    def calculatePercentage(self, params):
        sp.set_type(params,
            sp.TRecord(percentage = sp.TNat, amount = sp.TNat
        ))
        value = (params.percentage * params.amount) // 1000
        sp.result(value)

    # Core Functions
    @sp.entry_point
    def setAdmin(self, params):
        self._onlyAdmin()
        sp.set_type(params, sp.TAddress)
        self.data.admin = params

    @sp.entry_point
    def setRoyalty(self, params):
        self._onlyAdmin()
        sp.set_type(params, sp.TNat)
        self._checkValidRoyalty(params)
        self.data.royalty = params

    @sp.entry_point
    def setRoyaltyDivision(self, params):
        self._onlyAdmin()
        sp.set_type(params, sp.TRecord(
            thirdPartyToken = sp.TAddress,
            thirdPartyAdmin = sp.TAddress,
            toThirdParty = sp.TNat,
            toAdmin = sp.TNat
        ))
        sp.verify((params.toThirdParty + params.toAdmin) == sp.nat(1000), self.error.invalidRoyalty())
        self.data.royaltyDivision[params.thirdPartyToken] = sp.record(
            toAdmin = params.toAdmin,
            toThirdParty = params.toThirdParty,
            thirdPartyAdmin = params.thirdPartyAdmin
        )

    @sp.entry_point
    def whitelist(self, _token):
        self._onlyAdmin()
        sp.set_type(_token , sp.TAddress)
        self.data.whitelist[_token] = True

    @sp.entry_point
    def createAuction(self, params):
        sp.set_type(params,sp.TRecord(
            token = sp.TAddress, tokenId = sp.TNat, amount = sp.TNat,
            basePrice = sp.TMutez, timePeriod = sp.TInt
        ))
        self._isWhitelisted(params.token)

        sp.verify(sp.utils.mutez_to_nat(params.basePrice) > sp.nat(0),self.error.invalidPrice())
        sp.verify(params.timePeriod > sp.int(0), self.error.invalidTimePeriod())

        self._transferTokens(
            params.token, 
            params.tokenId, 
            params.amount, 
            sp.source,
            sp.self_address
        )

        self.data.auctions[self.data.auctionId] = sp.record(
            token = params.token, tokenId = params.tokenId, amount = params.amount,
            basePrice = params.basePrice, seller = sp.source, timePeriod = sp.now.add_seconds(params.timePeriod)
        )
        
        self.data.auctionId += 1

    @sp.entry_point
    def bid(self, _auctionId):
        sp.set_type(_auctionId, sp.TNat)
        self._auctionExists(_auctionId)
        sp.verify(self._isAuctionActive(_auctionId), self.error.invalidAuction())
        self._isBidValid(_auctionId)

        self._updateBidder(_auctionId)

    @sp.entry_point
    def cancelAuction(self, _auctionId):
        sp.set_type(_auctionId, sp.TNat)
        self._auctionExists(_auctionId)
        self._ownerOnly(self.data.auctions[_auctionId].seller, sp.source)
        self._refundBid(_auctionId)
        self._transferTokens(
            self.data.auctions[_auctionId].token, 
            self.data.auctions[_auctionId].tokenId,
            self.data.auctions[_auctionId].amount,
            sp.self_address,
            sp.source
        )
        del self.data.auctions[_auctionId]
    
    @sp.entry_point
    def withDraw(self, _auctionId):
        sp.set_type(_auctionId, sp.TNat)
        self._auctionExists(_auctionId)
        sp.verify(~(self._isAuctionActive(_auctionId)), self.error.invalidAuction())
        currAuction = sp.local('auction', self.data.auctions[_auctionId])

        sp.if self.data.bids.contains(_auctionId):
            currBid = sp.local('bid',self.data.bids[_auctionId])
            sp.verify((sp.source == currBid.value.owner) | (sp.source == currAuction.value.seller),self.error.ownerOnly())
            
            del self.data.bids[_auctionId]
            del self.data.auctions[_auctionId]

            royalty = sp.local('royalty', self.calculatePercentage(sp.record(percentage = self.data.royalty, amount = sp.utils.mutez_to_nat(currBid.value.value))))
            toTP = sp.local('toTP',0)
            toUs = sp.local('toUs',royalty.value)
            buyer = sp.local('buyer',currBid.value.owner)
            seller = sp.local('seller',currAuction.value.seller)
            toSeller = sp.utils.mutez_to_nat(currBid.value.value) - royalty.value

            sp.if self.data.royaltyDivision.contains(currAuction.value.token):
                toTP.value = self.calculatePercentage(
                    sp.record(
                        percentage = self.data.royaltyDivision[currAuction.value.token].toThirdParty, 
                        amount = royalty.value
                    )
                )
                toUs.value = self.calculatePercentage(
                    sp.record(
                        percentage = self.data.royaltyDivision[currAuction.value.token].toAdmin, 
                        amount = royalty.value
                    )
                )

            self._transferTokens(
                currAuction.value.token, 
                currAuction.value.tokenId,
                currAuction.value.amount,
                sp.self_address,
                buyer.value
            )
            
            self._transferRoyalty(
                toUs.value, 
                toTP.value,
                self.data.royaltyDivision[currAuction.value.token].thirdPartyAdmin
            )

            sp.send(
                seller.value,
                sp.utils.nat_to_mutez(sp.as_nat(toSeller))
            )
            
        sp.else :
            sp.verify(sp.source == currAuction.value.seller,self.error.ownerOnly())
            
            del self.data.auctions[_auctionId]

            self._transferTokens(
                currAuction.value.token, 
                currAuction.value.tokenId,
                currAuction.value.amount,
                sp.self_address,
                currAuction.value.seller
            )
    
    @sp.entry_point
    def create_listing(self,params):
        sp.set_type(params, sp.TRecord(
           token= sp.TAddress, 
           tokenId= sp.TNat, 
           
           amount= sp.TNat, 
           price_per_unit= sp.TNat))

        #check atleast one edition is minted
        sp.verify(params.amount > 0)
        
        # rename price_per_unti to price
        # check whitelisting : reffer create auction func

        #Check if the base price is not 0 
        sp.verify(params.price_per_unit > 0)

        #whitelisting

        self._transferTokens(
            params.token,
            params.tokenId,
            params.amount,
            sp.source,
            sp.self_address
        )

        self.data.listings[self.data.listingId] = sp.record(
            token= params.token, 
            tokenId= params.tokenId, 
            amount= params.amount, 
            price_per_unit= params.price_per_unit, 
            seller=sp.sender,
        )
        self.data.listingId += 1

    
    @sp.entry_point
    def collect(self, _listingId):

        sp.set_type(_listingId, sp.TNat)
        sp.verify(self.data.listings.contains(_listingId))

        #check buyer is not same as seller
        sale = sp.local("listings", self.data.listings[_listingId])
        sp.verify(sp.sender != sale.value.issuer)

        #check if xtz amount sent is equal to price defined while minting
        sp.verify(sp.amount == sale.value.price_per_unit)

        #check if atleast one edition is available to collect
        #sp.verify(sale.value.amount > 0)

        # calculate and send royalty : reffer withdraw func. above

        #price per token to be changed to price
        
#         with sp.if_(sale.value.price_per_unit != sp.tez(0)):

#             royalties_amount=sp.local("royalties_amount", sp.split_tokens(sale.value.price_per_token, sale.value.royalty, 1000))

#             with sp.if_(royalties_amount.value > sp.mutez(0)):
#                 sp.send(sale.value.creator, royalties_amount.value)


        self._transferTokens(
            sale.value.token,
            sale.value.tokenId,
            sale.value.amount,
            sp.self_address,
            sp.sender
        )

        sp.send(sale.value.creator, sp.amount-royalties_amount.value)

        self.data.sale[_listingId].amount = sp.as_nat(sale.value.amount - 1)

    
    @sp.entry_point
    def cancel_swap(self, _listingId):

        sp.set_type(_listingId, sp.TNat)
        sp.verify(self.data.sale.contains(_listingId))

        sale = sp.local("listings", self.data.sale[_listingId])
        # change from creator and issuer to seller
        sp.verify(sp.sender == sale.value.creator)

        # no need for this here
        sp.verify(sale.value.amount > 0)

        # return locked tokesn : reffer cancel auction

        del self.data.sale[_listingId]

        


        




        
