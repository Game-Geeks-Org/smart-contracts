import smartpy as sp

FA12 = sp.io.import_script_from_url('https://smartpy.io/templates/FA1.2.py')
FA2 = sp.io.import_script_from_url("https://smartpy.io/templates/FA2.py")


####################################################################################################
####################################################################################################

class GameGeeksToken(FA12.FA12):
    @sp.entry_point
    def market_transfer(self,params):
        sp.set_type_expr(params,Ingame_tkn_types.get_market_transfer_type())
        sp.verify(sp.sender == params.fa2_contract_address,message = "Cannot be called by this user")
        sp.verify(self.data.balances.contains(params.buyer),message="Buyer doesnot exist")
        sp.verify(self.data.balances.contains(params.seller),message="Seller doesnot exist")
        sp.verify(self.data.balances[params.buyer].balance >= params.price_in_gage,message="Insufficent Balance")
        # sp.verify(self.data.balances[params.from_].balance >= params.value, FA12_Error.InsufficientBalance)
        self.data.balances[params.buyer].balance = sp.as_nat(self.data.balances[params.buyer].balance - params.price_in_gage)
        self.data.balances[params.seller].balance += params.price_in_gage

####################################################################################################
####################################################################################################

class Ingame_tkn_types:
    def get_create_sale_type():
        return sp.TRecord(
            token_id = sp.TNat, 
            seller = sp.TAddress,
            price_in_gage = sp.TNat
        )
    def get_buy_from_sale_type():
        return sp.TRecord(
            token_id = sp.TNat, 
            buyer = sp.TAddress
        )
    def get_market_transfer_type():
        return sp.TRecord(
            fa2_contract_address = sp.TAddress,
            price_in_gage = sp.TNat,
            buyer = sp.TAddress,
            seller = sp.TAddress
        )
    def get_update_sale_type():
        return sp.TRecord(
            token_id = sp.TNat, 
            price_in_gage = sp.TNat
        )

####################################################################################################
####################################################################################################

class Display_tkn_types:
    def get_mint_type():
        return sp.TRecord(
            to_ = sp.TAddress,
            token_id = sp.TNat,
            is_badge = sp.TBool,
            amount = sp.TNat,
            metadata = sp.TMap(sp.TString, sp.TBytes)
        )
    def get_create_sale_type():
        return sp.TRecord(
            token_id = sp.TNat, 
            seller = sp.TAddress,
            price_in_mutez = sp.TMutez,
        )
    def get_buy_from_sale_type():
        return sp.TRecord(
            token_id = sp.TNat, 
            buyer = sp.TAddress
        )
    def get_market_transfer_type():
        return sp.TRecord(
            fa2_contract_address = sp.TAddress,
            price_in_mutez = sp.TMutez,
            buyer = sp.TAddress,
            seller = sp.TAddress
        )
    def get_update_sale_type():
        return sp.TRecord(
            token_id = sp.TNat, 
            price_in_mutez = sp.TMutez,
        )

####################################################################################################
####################################################################################################

# ADD TWO LISTS IN USERS TO SEPERATE BADGES FROM NFTS

class Display_token(FA2.FA2):
    def __init__(self, config, metadata, admin):
        FA2.FA2.__init__(self, config, metadata, admin)
        self.update_initial_storage(
            #Stores all the sales of display tokens that are currently available
            market_sales = sp.big_map(
                l = {},
                tkey = sp.TNat, 
                tvalue = sp.TRecord(
                    token_id = sp.TNat,
                    price_in_mutez = sp.TMutez, 
                    seller = sp.TAddress,
                    createdOn = sp.TTimestamp
                )
            ),
            # To differentiate badge NFTs from normal NFTs 
            badges = sp.set(t = sp.TNat),
            
            # Maintain a seperate map for game contract addresses and the respective tokens it creates.
            game_lookup = sp.big_map(l = {}, tkey = sp.TAddress, tvalue = sp.TList(sp.TNat))
        )
####################################################################################################

    @sp.entry_point
    def add_game_contract(self, params):
        sp.set_type_expr(params.game_contract_address,sp.TAddress)
        
        sp.verify(self.is_administrator(sp.sender),message="Non-admin")
        sp.verify(~self.data.game_lookup.contains(params.game_contract_address),message="Duplicate Entry")
        
        self.data.game_lookup[params.game_contract_address] = sp.list({})

####################################################################################################

    @sp.entry_point
    def mint(self, params):
        sp.set_type_expr(params,Display_tkn_types.get_mint_type())

        sp.verify(~self.is_paused(),message="transactions paused")
        
        sp.if params.is_badge:
            sp.verify(self.data.game_lookup.contains(sp.sender), message = "not game admin")
            self.data.badges.add(params.token_id)
            self.data.badges.add(params.token_id)
        sp.else:
            sp.verify(self.is_administrator(sp.sender), message = "transactions paused")
            sp.verify(params.amount == 1, message = "NFT-asset: amount <> 1")
            sp.verify(
                ~ self.token_id_set.contains(self.data.all_tokens, params.token_id),
                message = "NFT-asset: cannot mint twice same token"
            )

        user = self.ledger_key.make(params.to_, params.token_id)
        sp.if self.data.ledger.contains(user):
            self.data.ledger[user].balance += 1
        sp.else:
            self.data.ledger[user] = FA2.Ledger_value.make(1)

        sp.if ~ self.token_id_set.contains(self.data.all_tokens, params.token_id):
            self.token_id_set.add(self.data.all_tokens, params.token_id)
            self.data.token_metadata[params.token_id] = sp.record(
                token_id    = params.token_id,
                token_info  = params.metadata
            )
        if self.config.store_total_supply:
            self.data.total_supply[params.token_id] = params.amount + self.data.total_supply.get(params.token_id, default_value = 0)        

####################################################################################################
 

    @sp.entry_point
    def create_sale(self, params):
        sp.set_type_expr(params,Display_tkn_types.get_create_sale_type())
        
        sp.verify(~self.data.badges.contains(params.token_id),message = "This token is not for sale")
        sp.verify(self.data.total_supply.contains(params.token_id), message = "Token undefined")
    #     #Add the tz part in verifcation of invalid values

        sp.verify(params.price_in_mutez > sp.mutez(0), message = "INVALID_PRICE")
        
        seller = self.ledger_key.make(sp.sender, params.token_id)
        
        sp.verify(self.data.ledger.get(seller, sp.record(balance = 0)).balance >= 1, message = "INSUFFICIENT_BALANCE")
        sp.verify(~ self.data.market_sales.contains(params.token_id), message = "Duplicate Sale")
        
        self.data.market_sales[params.token_id] = sp.record(
            token_id = params.token_id,
            price_in_mutez = params.price_in_mutez, 
            seller = params.seller,
            createdOn = sp.now
        )

####################################################################################################

    @sp.entry_point
    def update_sale(self, params):
        sp.set_type_expr(params, Display_tkn_types.get_update_sale_type())

        sp.verify(self.data.market_sales.contains(params.token_id), message = "Sale does not exist")
        sale = self.data.market_sales[params.token_id]
        sp.verify(sale.seller == sp.sender, message = "You are not the seller")
        
        seller = self.ledger_key.make(sp.sender, params.token_id)
        sp.verify(self.data.ledger.get(seller, sp.record(balance = 0)).balance >= 1, message = "INSUFFICIENT_BALANCE")
        
        sp.verify(params.price_in_mutez > sp.mutez(0), message = "INVALID_PRICE")
        
        self.data.market_sales[params.token_id].price_in_mutez = params.price_in_mutez
        # self.data.market_sales[params.token_id].price_in_gage = params.price_in_gage

####################################################################################################

    @sp.entry_point
    def remove_sale(self, params):
        sp.set_type(params.token_id, sp.TNat)
        sp.verify(self.data.market_sales.contains(params.token_id), message = "Sale does not exist")
        sale = self.data.market_sales[params.token_id]
        sp.verify(sale.seller == sp.sender, message = "You are not the seller")
        del self.data.market_sales[params.token_id]
    
    @sp.entry_point
    def buy_from_sale(self, params):    
        sp.set_type_expr(params, Display_tkn_types.get_buy_from_sale_type())
        
        sp.verify(params.buyer == sp.sender,message = "Buyer and sender are not the same")
        sp.verify(self.data.market_sales.contains(params.token_id),message = "Sale does not exist")
        sp.verify(~self.data.badges.contains(params.token_id),message="cannot be bought")
        
        sale = self.data.market_sales[params.token_id]
        
        from_user = self.ledger_key.make(sale.seller, params.token_id)
        to_user = self.ledger_key.make(params.buyer, params.token_id)
        # sp.verify(self.data.all_tokens.contains(params.token_id), message = "TOKEN_UNDEFINED")

        current_balance = self.data.ledger.get(from_user, sp.record(balance = 0)).balance
        sp.verify(current_balance > 0, message = "User not selling this NFT")
        sp.verify(sp.amount == sale.price_in_mutez,message = "Price of the NFT is not matched")

        sp.send(self.data.market_sales[params.token_id].seller, self.data.market_sales[params.token_id].price_in_mutez)
        
        sp.if self.data.ledger.contains(to_user):
            self.data.ledger[to_user].balance += 1
        sp.else:
            self.data.ledger[to_user] = FA2.Ledger_value.make(1)
        
        self.data.ledger[from_user].balance = sp.as_nat(self.data.ledger[from_user].balance-1)
        del self.data.market_sales[params.token_id]

####################################################################################################
####################################################################################################

class Ingame_token(FA2.FA2):
    def __init__(self, config, metadata, admin, fa12_address):
        FA2.FA2.__init__(self, config, metadata, admin)
        self.update_initial_storage(
            ingame_sales = sp.big_map(
                l = {},
                tkey = sp.TNat, 
                tvalue = sp.TRecord(
                    token_id = sp.TNat,
                    # price_in_mutez = sp.TMutez, 
                    price_in_gage = sp.TNat, 
                    seller = sp.TAddress,
                    createdOn = sp.TTimestamp
                )
            ),
            fa12_contract_address = fa12_address,
            game_admins = sp.list(t = sp.TString)
        )
####################################################################################################

    @sp.entry_point
    def create_sale(self, params):
        sp.set_type_expr(params,Ingame_tkn_types.get_create_sale_type())

        sp.verify(self.data.total_supply.contains(params.token_id), message = "Token undefined")
    #     #Add the tz part in verifcation of invalid values
        sp.verify(params.price_in_gage > 0, message = "INVALID_PRICE")
        
        seller = self.ledger_key.make(sp.sender, params.token_id)
        sp.verify(self.data.ledger.get(seller, sp.record(balance = 0)).balance >= 1, message = "INSUFFICIENT_BALANCE")
        
    #     market_place = sp.contract(Ingame_tkn_types.get_add_to_sale_type(), params.market_address, entry_point = "add_to_sale").open_some()
        sp.verify(~ self.data.ingame_sales.contains(params.token_id), message = "Duplicate Sale")
        self.data.ingame_sales[params.token_id] = sp.record(
            token_id = params.token_id,
            # price_in_mutez = params.price_in_mutez, 
            price_in_gage = params.price_in_gage, 
            seller = params.seller,
            createdOn = sp.now
        )

####################################################################################################

    @sp.entry_point
    def update_sale(self, params):
        sp.set_type_expr(params, Ingame_tkn_types.get_update_sale_type())

        sp.verify(self.data.ingame_sales.contains(params.token_id), message = "Sale does not exist")
        sale = self.data.ingame_sales[params.token_id]
        sp.verify(sale.seller == sp.sender, message = "You are not the seller")
        
        seller = self.ledger_key.make(sp.sender, params.token_id)
        sp.verify(self.data.ledger.get(seller, sp.record(balance = 0)).balance >= 1, message = "INSUFFICIENT_BALANCE")
        
        sp.verify(params.price_in_gage > 0, message = "INVALID_PRICE")
        
        # self.data.ingame_sales[params.token_id].price_in_mutez = params.price_in_mutez
        self.data.ingame_sales[params.token_id].price_in_gage = params.price_in_gage

####################################################################################################

    @sp.entry_point
    def remove_sale(self, params):
        sp.set_type(params, sp.TRecord(token_id = sp.TNat))
        sp.verify(self.data.ingame_sales.contains(params.token_id), message = "Sale does not exist")
        sale = self.data.ingame_sales[params.token_id]
        sp.verify(sale.seller == sp.sender, message = "You are not the seller")
        del self.data.ingame_sales[params.token_id]

####################################################################################################

    @sp.entry_point
    def buy_from_sale(self, params):    
        sp.set_type_expr(params, Ingame_tkn_types.get_buy_from_sale_type())
        sp.verify(params.buyer == sp.sender,message = "Buyer and sender are not the same")
        sp.verify(self.data.ingame_sales.contains(params.token_id),message = "Sale does not exist")
        sale = self.data.ingame_sales[params.token_id]
        
        from_user = self.ledger_key.make(sale.seller, params.token_id)
        to_user = self.ledger_key.make(params.buyer, params.token_id)
        # sp.verify(self.data.all_tokens.contains(params.token_id), message = "TOKEN_UNDEFINED")
        
        current_balance = self.data.ledger.get(from_user, sp.record(balance = 0)).balance
        sp.verify(current_balance > 0, message = "User not selling this NFT")
        
        fa12_contract = sp.contract(Ingame_tkn_types.get_market_transfer_type(),self.data.fa12_contract_address,entry_point = "market_transfer").open_some() 
        sp.transfer(sp.record
                            (
                                fa2_contract_address = sp.self_address,
                                price_in_gage = sale.price_in_gage,
                                buyer = params.buyer,
                                seller = sale.seller 
                            ), 
                        sp.mutez(0), 
                        fa12_contract
                    )

        sp.if self.data.ledger.contains(to_user):
            self.data.ledger[to_user].balance += 1
            self.data.ledger[from_user].balance = 0
        sp.else:
            self.data.ledger[to_user] = FA2.Ledger_value.make(1)
            self.data.ledger[from_user].balance = 0

        del self.data.ingame_sales[params.token_id]

####################################################################################################
####################################################################################################

# ################################ Test Scenarios ##################################################
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
        # contract_metadata = sp.utils.metadata_of_url("ipfs://bafkreicysfopd2fnmytjgsagdk555mh6d2npfqrbtlbxfj7srwzayd2maq")
    )
    # IPFS Hash for contract_metadata: bafkreicysfopd2fnmytjgsagdk555mh6d2npfqrbtlbxfj7srwzayd2maq
    scenario = sp.test_scenario()   
    
    # scenario += geekcoin
    
    # geekcoin.mint(sp.record(address = elon.address,value = sp.nat(2000))).run(sender = admin1.address)
    # geekcoin.mint(sp.record(address = mark.address,value = sp.nat(1000))).run(sender = admin1.address)
    # geekcoin.burn(sp.record(address = elon.address,value = sp.nat(10))).run(sender = admin1.address)
    # geekcoin.transfer(sp.record(from_ = elon.address,to_ = mark.address,value = sp.nat(10))).run(sender=elon.address)

    ingame_token = Ingame_token(
        FA2.FA2_config(single_asset = False, non_fungible=True,assume_consecutive_token_ids = True),
        admin = admin1.address,
        metadata = sp.utils.metadata_of_url("ipfs://xxxxxxxxxxxxxxxxxxxxxxxxxx"),
        fa12_address = geekcoin.address
    )

    nft1_metadata = {
        "name" : sp.utils.bytes_of_string("First NFT #1"),
        "symbol" : sp.utils.bytes_of_string("FNFT"),
        "decimals" : sp.utils.bytes_of_string("0"),
        "artifactUri" : sp.utils.bytes_of_string("ipfs://abcdefg"),
        "displayUri" : sp.utils.bytes_of_string("ipfs://abcdefg"),
        "thumbnailUri" : sp.utils.bytes_of_string("ipfs://abcdefg"),
        "metadata" : sp.utils.bytes_of_string("ipfs://abcdefg")
    }
    
    nft2_metadata = {
        "name" : sp.utils.bytes_of_string("Seconf NFT #2"),
        "symbol" : sp.utils.bytes_of_string("SNFT"),
        "decimals" : sp.utils.bytes_of_string("0"),
        "artifactUri" : sp.utils.bytes_of_string("ipfs://abcdefg"),
        "displayUri" : sp.utils.bytes_of_string("ipfs://abcdefg"),
        "thumbnailUri" : sp.utils.bytes_of_string("ipfs://abcdefg"),
        "metadata" : sp.utils.bytes_of_string("ipfs://abcdefg")
    }
        
    nft3_metadata = {
        "name" : sp.utils.bytes_of_string("Third NFT #3"),
        "symbol" : sp.utils.bytes_of_string("TNFT"),
        "decimals" : sp.utils.bytes_of_string("0"),
        "artifactUri" : sp.utils.bytes_of_string("ipfs://abcdefg"),
        "displayUri" : sp.utils.bytes_of_string("ipfs://abcdefg"),
        "thumbnailUri" : sp.utils.bytes_of_string("ipfs://abcdefg"),
        "metadata" : sp.utils.bytes_of_string("ipfs://abcdefg")
    }
    display_token = Display_token(
        FA2.FA2_config(single_asset = False, non_fungible=True,assume_consecutive_token_ids = True),
        admin = admin1.address,
        metadata = sp.utils.metadata_of_url("ipfs://xxxxxxxxxxxxxxxxxxxxxxxxxx")
    )
    scenario += display_token
    scenario += display_token.mint(to_ = admin1.address,amount = 1,metadata = nft1_metadata,token_id = 0,is_badge = False).run(sender = admin1)
    scenario += display_token.mint(to_ = admin1.address,amount = 1,metadata = nft1_metadata,token_id = 1,is_badge = False).run(sender = admin1)
    scenario += display_token.mint(to_ = admin1.address,amount = 1,metadata = nft1_metadata,token_id = 2,is_badge = False).run(sender = admin1)
    
    display_token.transfer([
            ingame_token.batch_transfer.item(
                from_ = admin1.address,
                txs = [sp.record(to_ = elon.address,amount = 1,token_id = 0),sp.record(to_ = elon.address,amount = 1,token_id = 1),sp.record(to_ = mark.address,amount = 1,token_id = 2)]
            )
        ]).run(sender = admin1.address)

    scenario += display_token.create_sale(token_id = 0,price_in_mutez = sp.mutez(1000000),seller = elon.address).run(sender = elon.address)
    scenario += display_token.update_sale(token_id = 0,price_in_mutez = sp.mutez(1000)).run(sender = elon.address)
    scenario += display_token.buy_from_sale(token_id = 0,buyer = mark.address).run(sender = mark.address,amount = sp.mutez(100000),valid = False)
    scenario += display_token.buy_from_sale(token_id = 0,buyer = mark.address).run(sender = mark.address,amount = sp.mutez(1000))
    


    # scenario += ingame_token

    # scenario.p("admin mints NFT 1 to self")
    # ingame_token.mint(address = admin1.address,amount = 1,metadata = nft1_metadata,token_id = 0).run(sender = admin1)
    # scenario.p("admin mints NFT 2 to self")
    # ingame_token.mint(address = admin1.address,amount = 1,metadata = nft2_metadata,token_id = 1).run(sender = admin1)    
    # scenario.p("admin mints NFT 3 to self")
    # ingame_token.mint(address = admin1.address,amount = 1,metadata = nft3_metadata,token_id = 2).run(sender = admin1)

    # scenario.p("admin transfers NFT to mark")
    # ingame_token.transfer([
    #             ingame_token.batch_transfer.item(
    #                 from_ = admin1.address,
    #                 txs = [sp.record(to_ = mark.address,amount = 1,token_id = 0),sp.record(to_ = elon.address,amount = 1,token_id = 1)]
    #             )
    #         ]).run(sender = admin1.address)


    # # market = MarketPlace(fa2_contract_address = ingame_token.address,metadata="")
    # # scenario += market    
    # scenario += ingame_token.create_sale(seller = elon.address,
    #             token_id = 1, 
    #             # price_in_mutez = sp.mutez(0),
    #             price_in_gage = 3000
    #         ).run(sender = elon.address)

    # scenario += ingame_token.update_sale(token_id = 1,price_in_gage = 300).run(sender = elon.address)
    # scenario += ingame_token.remove_sale(token_id = 1).run(sender = elon.address)
    
    # scenario += ingame_token.create_sale(seller = elon.address,
    #             token_id = 1, 
    #             price_in_gage = 3000
    #         ).run(sender = elon.address)
    
    # scenario += ingame_token.update_sale(token_id = 1,price_in_gage = 200).run(sender = elon.address)

    # scenario += ingame_token.buy_from_sale(token_id = sp.nat(1), buyer = mark.address).run(sender = mark.address)