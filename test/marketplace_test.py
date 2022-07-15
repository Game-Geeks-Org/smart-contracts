import smartpy as sp

Marketplace = sp.io.import_stored_contract("marketplace")
fa2 = sp.io.import_stored_contract("fa2")

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

    c = Marketplace.marketplace(admin = admin1.address,_royalty =  sp.nat(1))
    scenario += c
    scenario += nft1

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

