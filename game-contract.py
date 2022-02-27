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
                    total_value_locked = sp.TString,
                    admins = sp.set(l=[admin_address],t=sp.TAddress),
                    number_of_games = sp.TNat
                )
            ),
        )


# ################################ ADD NEW GAME ####################################
    @sp.entry_point
    def add_game(self,params):
        sp.set_type(params.game_address,sp.TAddress)
        sp.set_type(params.name,sp.TString)

        sp.verify(sp.source==params.game_address, message = "Game")        
        sp.verify(self.data.games.contains(params.game_address)==False, message = "Game already exists with this wallet address")
        
        self.data.games[params.game_address] = sp.record(
            name = params.user_name, 
            description = "",
            is_active = sp.bool(False),
            number_of_games_played = sp.nat(0),
            total_value_locked = "",
             number_of_games = sp.nat(0)
        )
        
        
 # ################################ ADD NEW ADMIN ####################################            
    @sp.entry_point
    def add_admin(self,params):
        sp.set_type(params.new_admin_address,sp.TAddress)

        sp.verify(self.data.admins.contains(sp.source), message = "Entrypoint called by non-admin user")
        sp.verify(self.data.admins.contains(params.new_admin_address) == False, message = "This address already has admin privileges")
        
        self.data.admins.add(params.new_admin_address)
