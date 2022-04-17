import smartpy as sp

class Game(sp.Contract):
    def __init__(self,admin_address):
        self.init(
            games = sp.big_map(
                tkey = sp.TAddress,
                tvalue = sp.TRecord(
                    name = sp.TString, #Unique string for each user
                    description = sp.TString,
                    is_active = sp.TBool,
                    number_of_games_played = sp.TNat,
                    total_value_locked = sp.TNat,
                    admins = sp.TSet(t = sp.TAddress),
                )
            ),
            number_of_games = sp.nat(0),
            admins = sp.set(l=[admin_address],t=sp.TAddress),
        )


################################## ADD NEW GAME ####################################
    @sp.entry_point
    def add_game(self,params):
        sp.set_type(params.game_address,sp.TAddress)
        sp.set_type(params.name,sp.TString)
        sp.set_type(params.admin,sp.TAddress)
        sp.set_type(params.description,sp.TString)

        sp.verify(sp.source==params.game_address, message = "Game")        
        sp.verify(self.data.games.contains(params.game_address)==False, message = "Game already exists with this wallet address")
        
        self.data.games[params.game_address] = sp.record(
            name = params.name, 
            description = params.description,
            is_active = sp.bool(False),
            number_of_games_played = sp.nat(0),
            total_value_locked = sp.nat(0),
            admins = sp.set([params.admin])
        )
        self.data.number_of_games += 1

################################## Update description ####################################
    @sp.entry_point
    def update_description(self,params):
        sp.set_type(params.game_address,sp.TAddress)
        sp.set_type(params.description,sp.TString)

        sp.verify(self.data.games.contains(params.game_address), message = "Game doesnot exist with this address")
        sp.verify(self.data.games[params.game_address].admins.contains(sp.source), message = "Game doesnot exist with this address")

        self.data.games[params.game_address].description = params.description


################################## Update is_active ####################################
    @sp.entry_point
    def set_is_active(self,params):
        sp.set_type(params.game_address,sp.TAddress)
        sp.set_type(params.is_active,sp.TBool)
        # sp.set_type(sp.source,sp.TAddress)

        sp.verify(self.data.games.contains(params.game_address), message = "Game doesnot exist with this address")
        sp.verify(self.data.games[params.game_address].admins.contains(sp.source), message = "Game doesnot exist with this address")

        self.data.games[params.game_address].is_active = params.is_active
        
        
################################### ADD NEW ADMIN ####################################            
    @sp.entry_point
    def add_admin_to_a_game(self,params):
        sp.set_type(params.new_admin_address,sp.TAddress)
        sp.set_type(params.game_address,sp.TAddress)

        sp.verify(self.data.games.contains(params.game_address), message = "Game doesnot exist with this address")
        sp.verify(self.data.games[params.game_address].admins.contains(sp.source), message = "Entrypoint called by non-admin user")
        sp.verify(self.data.games[params.game_address].admins.contains(params.new_admin_address) == False, message = "This address already has admin privileges")
        
        self.data.games[params.game_address].admins.add(params.new_admin_address)

 # ################################ ADD NEW ADMIN TO CONTRACT####################################            
    @sp.entry_point
    def add_admin_to_contract(self,params):
        sp.set_type(params.new_admin_address,sp.TAddress)

        sp.verify(self.data.admins.contains(sp.source), message = "Entrypoint called by non-admin user")
        sp.verify(self.data.admins.contains(params.new_admin_address) == False, message = "This address already has admin privileges")
        
        self.data.admins.add(params.new_admin_address)

# ################################ update total value locked ####################################            
    @sp.entry_point
    def update_total_value_locked(self,params):
        sp.set_type(params.game_address,sp.TAddress)
        sp.set_type(params.new_value,sp.TNat)

        sp.verify(self.data.games.contains(params.game_address), message = "Game doesnot exist")
        sp.verify(self.data.games[params.game_address].admins.contains(sp.source), message = "Need admin privileges")
        
        self.data.games[params.game_address].total_value_locked = params.new_value

# ################################ increment number of games ####################################            
    @sp.entry_point
    def incr_number_of_games_played(self,params):
        sp.set_type(params.game_address,sp.TAddress)

        sp.verify(self.data.games.contains(params.game_address), message = "Game doesnot exist")
        sp.verify(self.data.games[params.game_address].admins.contains(sp.source), message = "Need admin privileges")
        
        self.data.games[params.game_address].number_of_games_played += 1

################################## TESTS ####################################            
@sp.add_test(name="game_test")
def test():
    scenario = sp.test_scenario()

    admin1 = sp.test_account("admin1")
    admin2 = sp.test_account("admin2")
    
    game_admin1 = sp.test_account("game_admin1")
    game_admin2 = sp.test_account("game_admin2")
    game2_admin = sp.test_account("game2_admin")
    
    game1 = sp.test_account("game1")
    game2 = sp.test_account("game2")
    game3 = sp.test_account("game3")
    mark = sp.test_account("mark")
    
    game_contract = Game(admin1.address)    

    scenario += game_contract
    
    scenario += game_contract.add_game(admin = game_admin1.address,game_address = game1.address,name = sp.string("Space Shooter"), description = sp.string("Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem ")).run(sender = mark,valid = False)
    scenario += game_contract.add_game(admin = game_admin1.address,game_address = game1.address,name = sp.string("Space Shooter"), description = sp.string("Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem ")).run(sender = game1,valid = True)
    scenario += game_contract.add_game(admin = game_admin1.address,game_address = game1.address,name = sp.string("Space Shooter"), description = sp.string("Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem ")).run(sender = game1,valid = False)
    scenario += game_contract.add_game(admin = game2_admin.address,game_address = game2.address,name = sp.string("Subway Surfers"), description = sp.string("Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem Lorem ipsm Dorem ")).run(sender = game2,valid = True)
    

    scenario += game_contract.add_admin_to_contract(new_admin_address = admin1.address).run(sender = admin1.address,valid = False) 
    scenario += game_contract.add_admin_to_contract(new_admin_address = admin1.address).run(sender = mark.address,valid = False) 
    scenario += game_contract.add_admin_to_contract(new_admin_address = admin2.address).run(sender = admin1.address,valid = True) 

    scenario += game_contract.add_admin_to_a_game(new_admin_address = game_admin1.address,game_address = mark.address).run(sender = game_admin1.address, valid = False) 
    scenario += game_contract.add_admin_to_a_game(new_admin_address = game_admin1.address,game_address = game1.address).run(sender = game_admin1.address, valid = False) 
    scenario += game_contract.add_admin_to_a_game(new_admin_address = game_admin2.address,game_address = game1.address).run(sender = mark.address, valid = False) 
    scenario += game_contract.add_admin_to_a_game(new_admin_address = game_admin2.address,game_address = game1.address).run(sender = game_admin1.address,valid = True) 

    scenario += game_contract.set_is_active(game_address = mark.address, is_active = True).run(sender = mark,valid = False)
    scenario += game_contract.set_is_active(game_address = game1.address, is_active = True).run(sender = mark,valid = False)
    scenario += game_contract.set_is_active(game_address = game1.address, is_active = True).run(sender = game_admin1,valid = True)
    
    scenario += game_contract.update_total_value_locked(game_address = mark.address, new_value = sp.nat(10)).run(sender = game_admin1,valid = False)
    scenario += game_contract.update_total_value_locked(game_address = game1.address, new_value = sp.nat(10)).run(sender = mark,valid = False)
    scenario += game_contract.update_total_value_locked(game_address = game1.address, new_value = sp.nat(10)).run(sender = game_admin1,valid = True)
    scenario += game_contract.update_total_value_locked(game_address = game2.address, new_value = sp.nat(40)).run(sender = game2_admin,valid = True)
    
    scenario += game_contract.incr_number_of_games_played(game_address = game1.address).run(sender = game_admin1,valid = True)
    scenario += game_contract.incr_number_of_games_played(game_address = game1.address).run(sender = game_admin1,valid = True)
    scenario += game_contract.incr_number_of_games_played(game_address = game1.address).run(sender = game2_admin,valid = False)
    scenario += game_contract.incr_number_of_games_played(game_address = game2.address).run(sender = game2_admin,valid = True)
    