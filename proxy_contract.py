import smartpy as sp

class Proxy_contract(sp.Contract):
    def __init__(self,admin,gage_coin_contract_address,ingame_tkn_contract_address,display_tkn_contract_address,user_contract_address):
        self.init(
            super_admin = admin,
            gage_coin_contract_address = gage_coin_contract_address,
            ingame_tkn_contract_address = ingame_tkn_contract_address,
            display_tkn_contract_address = display_tkn_contract_address,
            user_contract_address = user_contract_address,
            game_contracts = sp.set(t = sp.TAddress)
        )
    
    @sp.entry_point
    def add_game_contract_address(self,params):
        sp.set_type(params.game_contract_address, sp.TAddress)
        sp.verify(~game_contracts.contains(params.game_contract_address),message = "Game contract already exists")
        game_contracts.add(params.game_contract_address)

    ################################ Account Management ##################################

    @sp.entry_point
    def add_user(self,params):
        sp.set_type(params.)
        sp.verify(params.new_user_address == sp.sender)
        user_contract = sp.contract(self.data.user_contract_address,entry_point = "add_user").open_some()
    
    @sp.entry_point
    def update_username(self,params):
        sp.set_type(params.)
        sp.verify(params.user_address == sp.sender)
        user_contract = sp.contract(self.data.user_contract_address,entry_point = "update_username").open_some()

    @sp.entry_point
    def update_profile_pic(self,params):
        sp.set_type(params.)
        sp.verify(params.user_address == sp.sender)
        user_contract = sp.contract(self.data.user_contract_address,entry_point = "update_profile_pic").open_some()

    @sp.entry_point
    def 


    ################################ Account Management End ##################################

    ################################ SETTERS ##################################

    @sp.entry_point
    def update_gage_coin_contract_address(self,params):
        sp.set_type(params.gage_coin_contract_address, sp.TAddress)
        sp.verify(sp.sender == self.data.super_admin,message = "Admin previleges required to update")
        self.data.gage_coin_contract_address = params.gage_coin_contract_address

    @sp.entry_point
    def update_ingame_tkn_contract_address(self,params):
        sp.set_type(params.ingame_tkn_contract_address, sp.TAddress)
        sp.verify(sp.sender == self.data.super_admin,message = "Admin previleges required to update")
        self.data.ingame_tkn_contract_address = params.ingame_tkn_contract_address

    @sp.entry_point
    def update_display_tkn_contract_address(self,params):
        sp.set_type(params.display_tkn_contract_address, sp.TAddress)
        sp.verify(sp.sender == self.data.super_admin,message = "Admin previleges required to update")
        self.data.display_tkn_contract_address = params.display_tkn_contract_address

    @sp.entry_point
    def update_user_contract_address(self,params):
        sp.set_type(params.user_contract_address, sp.TAddress)
        sp.verify(sp.sender == self.data.super_admin,message = "Admin previleges required to update")
        self.data.user_contract_address = params.user_contract_address

    ################################ SETTERS END ##################################

@sp.add_test(name="proxy_test")
def test():
    scenario = sp.test_scenario()

    admin1 = sp.test_account("admin1")
    fa12_contract = sp.test_account("gamegeekcoin")
    ingame_tkn_contract = sp.test_account("ingameNFT")
    display_tkn_contract = sp.test_account("displayNFT")
    user_contract = sp.test_account("user_contract")
    game1 = sp.test_account("game1")
    
    proxy_contract = Proxy_contract(
            admin = admin1.address,
            gage_coin_contract_address = fa12_contract.address,
            ingame_tkn_contract_address = ingame_tkn_contract.address,
            display_tkn_contract_address = display_tkn_contract.address,
            user_contract_address = user_contract.address
        )

    scenario += proxy_contract
    
    scenario += user_contract.add_game_contract_address(game_contract_address=game1.address).run(sender = admin1.address)
    