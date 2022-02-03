import smartpy as sp

FA12 = sp.io.import_script_from_url('https://smartpy.io/templates/FA1.2.py')

class GameGeeksToken(FA12.FA12):
    pass

# ################################ Test Scenarios #################################    
@sp.add_test(name="fa12_token_test_1")
def test():
    admin1 = sp.test_account("admin1")
    game1 = sp.test_account("game1")
    mark = sp.test_account("mark")
    elon = sp.test_account("elon")
    
    token_metadata = {
        "name": "Game Geeks Token",
        "symbol": "GaGe",
        "decimals": "6"
    }
    
    geekcoin = GameGeeksToken(
        admin1.address, # Update the admin address before deployement to the chain. 
        config = FA12.FA12_config(),
        token_metadata = token_metadata,
        contract_metadata = sp.utils.metadata_of_url("ipfs://bafkreicysfopd2fnmytjgsagdk555mh6d2npfqrbtlbxfj7srwzayd2maq")
    )
    # IPFS Hash for contract_metadata: bafkreicysfopd2fnmytjgsagdk555mh6d2npfqrbtlbxfj7srwzayd2maq
    scenario = sp.test_scenario()   
    
    scenario += geekcoin
    
    geekcoin.mint(sp.record(address = elon.address,value = sp.nat(100))).run(sender = admin1.address)
    geekcoin.mint(sp.record(address = mark.address,value = sp.nat(10))).run(sender = admin1.address)
    geekcoin.burn(sp.record(address = elon.address,value = sp.nat(10))).run(sender = admin1.address)
    geekcoin.transfer(sp.record(from_ = elon.address,to_ = mark.address,value = sp.nat(10))).run(sender=elon.address)