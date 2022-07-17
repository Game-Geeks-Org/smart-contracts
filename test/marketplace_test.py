import smartpy as sp

Marketplace = sp.io.import_stored_contract("marketplace")
fa2 = sp.io.import_stored_contract("fa2")

def mintNFT(nft, id, to, admin):
    tok0_md = fa2.FA2.make_metadata(
            name = "The Token One",
            decimals = 0,
            symbol= "TK0" )
    nft.mint(
        address = to,
        amount = 1,
        metadata = tok0_md,
        token_id = id
    ).run(sender = admin)

def mintFT(ft, id, to, admin, amount):
    tok0_md = fa2.FA2.make_metadata(
            name = "The Token One",
            decimals = 6,
            symbol= "TK0" )
    ft.mint(
        address = to,
        amount = amount,
        metadata = tok0_md,
        token_id = id
    ).run(sender = admin)

def setOperator(token, owner, operator, id):
        token.update_operators([
                sp.variant("add_operator", token.operator_param.make(
                    owner = owner.address,
                    operator = operator.address,
                    token_id = id
                    )
                ),
            ]).run(sender = owner)

@sp.add_test(name = "GameGeeks Marketplace")
def test():
    scenario = sp.test_scenario()
    scenario.h1("GameGeeks Marketplace")

    admin1 = sp.test_account("admin1")
    admin2 = sp.test_account("admin2")
    user1 = sp.test_account("user1")
    user2 = sp.test_account("user2")

    nft1 = fa2.FA2(
            config = fa2.FA2_config(non_fungible = True),
            metadata = sp.utils.metadata_of_url("https://example.com"),
            admin = admin1.address
        )

    nft2 = fa2.FA2(
            config = fa2.FA2_config(non_fungible = True),
            metadata = sp.utils.metadata_of_url("https://example.com"),
            admin = admin1.address
        )

    ft1 = fa2.FA2(
            config = fa2.FA2_config(non_fungible = False),
            metadata = sp.utils.metadata_of_url("https://example.com"),
            admin = admin1.address
        )

    ft2 = fa2.FA2(
            config = fa2.FA2_config(non_fungible = False),
            metadata = sp.utils.metadata_of_url("https://example.com"),
            admin = admin1.address
        )

    c = Marketplace.marketplace(admin = admin1.address,_royalty =  sp.nat(1))
    scenario += c
    scenario += nft1
    scenario += nft2
    scenario += ft2
    scenario += ft1

    # ---------------- Set admin ---------------- #
    
    # it should not set admin if not called by the current admin
    c.setAdmin(user1.address).run(sender = user1, valid = False)

    # it should update admin
    c.setAdmin(admin2.address).run(sender = admin1)


    # --------------- Set Royalty -------------- #

    # it should not set royalty percentage if not called by the admin
    c.setRoyalty(10).run(sender = admin1, valid = False)

    # it should not set royalty if asking more than 100%
    c.setRoyalty(10000).run(sender = admin2, valid = False)

    # it should set royalty percentage
    c.setRoyalty(50).run(sender = admin2) 

    # --------------- Set Royalty Divistion -------------- #

    # it should not set division if not called by the admin
    c.setRoyaltyDivision(sp.record(
        thirdPartyToken = nft1.address,
        thirdPartyAdmin = user2.address,
        toThirdParty = 100,
        toAdmin = 900
    )).run(sender = user2, valid = False)

    # it should not set division if invalid params passed
    c.setRoyaltyDivision(sp.record(
        thirdPartyToken = nft1.address,
        thirdPartyAdmin = user2.address,
        toThirdParty = 10000,
        toAdmin = 1000
    )).run(sender = admin2, valid = False)

    # it should set division of royalty
    c.setRoyaltyDivision(sp.record(
        thirdPartyToken = nft1.address,
        thirdPartyAdmin = user2.address,
        toThirdParty = 300,
        toAdmin = 700
    )).run(sender = admin2)

    # ----------------- Create New Auction --------------

    mintNFT(nft1, 0, admin1.address, admin1)
    mintNFT(nft2, 0, user1.address, admin1)
    mintFT(ft1, 0, admin1.address, admin1, 100000000)

    # it should not create new auction if base price is 0
    c.createAuction(sp.record(
        token = nft1.address, tokenId = 0, amount = sp.nat(1),
        basePrice = sp.mutez(0), timePeriod = sp.int(86400)
    )).run(sender = admin1, valid = False)

    # it should not create new auction if time period if 0
    c.createAuction(sp.record(
        token = nft1.address, tokenId = 0, amount = sp.nat(1),
        basePrice = sp.mutez(100000), timePeriod = sp.int(0)
    )).run(sender = admin1, valid = False)

    # it should not create new auction if not called by the token owner
    c.createAuction(sp.record(
        token = nft1.address, tokenId = 0, amount = sp.nat(1),
        basePrice = sp.mutez(100000), timePeriod = sp.int(86400)
    )).run(sender = user1, valid = False)

    # it should create new auction with NFT, and transfer token to the vault
    setOperator(nft1, admin1, c, 0)
    c.createAuction(sp.record(
        token = nft1.address, tokenId = 0, amount = sp.nat(1),
        basePrice = sp.mutez(100000), timePeriod = sp.int(86400)
    )).run(sender = admin1)

    scenario.verify(nft1.data.ledger[nft1.ledger_key.make(c.address, 0)].balance == 1)
    scenario.verify(nft1.data.ledger[nft1.ledger_key.make(admin1.address, 0)].balance == 0)

    # it should create new auction with FT, and transfer token to the vault
    setOperator(ft1, admin1, c, 0)
    c.createAuction(sp.record(
        token = ft1.address, tokenId = 0, amount = sp.nat(100000),
        basePrice = sp.mutez(100), timePeriod = sp.int(86400)
    )).run(sender = admin1)

    scenario.verify(ft1.data.ledger[ft1.ledger_key.make(c.address, 0)].balance == 100000)


    # ----------------- New Bid --------------

    # it should not make bid if auction does not exist
    c.bid(sp.nat(3)).run(sender = user2, amount = sp.mutez(100000), valid = False)

    # it should not make bid if auction is expired

    # it should not make bid if 1st bid is less than base price
    c.bid(sp.nat(0)).run(sender = user1, amount = sp.mutez(10), valid = False)

    # it should make the first bid
    c.bid(sp.nat(0)).run(sender = user1, amount = sp.mutez(100000))

    # it should not make bid if it is less than current bid
    c.bid(sp.nat(0)).run(sender = user2, amount = sp.mutez(1000), valid = False)

    # it should make a bid, refund the previoud bidder and update the bid details
    c.bid(sp.nat(0)).run(sender = user2, amount = sp.mutez(1000000))    


    # --------------- Cancel Auction -----------

    # it should not cancel auction if it does not exist
    c.cancelAuction(5).run(sender = admin2, valid = False)

    # it should not cancel auction if not called by the auction owner
    c.cancelAuction(0).run(sender = user1, valid = False)

    # it should cancel auction, refund the bid if any, return the assets to the owner and delete this entry from the map
    c.cancelAuction(0).run(sender = admin1)
    scenario.verify(nft1.data.ledger[nft1.ledger_key.make(c.address, 0)].balance == 0)
    scenario.verify(nft1.data.ledger[nft1.ledger_key.make(admin1.address, 0)].balance == 1)


    #---------------- Withdraw ----------------

    


