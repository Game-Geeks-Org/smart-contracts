import smartpy as sp

class Error_message :
    def adminOnly(self):
        return  "ADMIN_ONLY"
    
    def invalidRoyalty(self):
        return "INVALID_ROYALTY"

'''
    NOTE: 
    1. Royalty percentage is calculated as follows:
        - if royalty is set as 10, this means royalty is 1%
        - to calculate the royalty amount, multiply the amount involved with royalty amount then divide by 1000
        - ie.    royaltyAmount = (amountInvolved * royalty)/1000
    2. Division of royalty between third party nfts and admin is also carried in the same way as described above
'''
class marketplace(sp.Contract):
    def __init__(self,admin, _royalty, metadata):
        self.error = Error_message()
        
        self.init_type(sp.TRecord(
            metadata=sp.TBigMap(sp.TString,sp.TBytes)
        ))
        self.init(
            metadata = metadata,
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
                seller = sp.TAddress, timePeriod = sp.TTimestamp
            )),
        )

    def _onlyAdmin(self):
        sp.verify(sp.sender == self.data.admin, self.error.adminOnly())

    def _checkValidRoyalty(self, amount):
        sp.verify(amount <= sp.nat(1000),self.error.invalidRoyalty())


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

    @sp.private_lambda(with_storage = 'read-write')
    def calculatePercentage(self, params):
        sp.set_type(params,
            sp.TRecord(percentage = sp.TNat, amount = sp.TNat
        ))
        value = (params.percentage * params.amount) // 1000
        sp.result(value)


