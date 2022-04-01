import smartpy as sp

class User_types:
    def add_user_type():
        return sp.TRecord(
            user_address = sp.TAddress, 
            user_name = sp.TString,
            profile_picture = sp.TString
        )
    
    def update_username_type():
        return sp.TRecord(
            user_address = sp.TAddress,
            new_user_name = sp.TString
        )       

    def update_pp_type():
        return sp.TRecord(
            user_address = sp.TAddress,
            ipfs_url = sp.TString
        )

    def add_user_to_game():
        return sp.TRecord(
            user_address = sp.TAddress,
            game_address = sp.TAddress
        )

class Game_types:
    def create_game_type():
        return sp.TRecord(
            game_address=sp.TAddress,
            name=sp.TString,
            admin=sp.TAddress,
            description=sp.TString
        ) 
    
    def update_description_type():
        return sp.TRecord(
            game_address=sp.TAddress,
            description=sp.TString
        ) 
    
    def set_is_active_type():
        return sp.TRecord(
            game_address=sp.TAddress,
            is_active=sp.TBool
        ) 
    def add_admin_to_a_game_type():
        return sp.TRecord(
            game_address=sp.TAddress,
            new_admin_address=sp.TAddress
        ) 
    def add_admin_to_game_contract_type():
        return sp.TRecord( 
            new_admin_address=sp.TAddress
        ) 
    def update_total_value_locked_type():
        return sp.TRecord( 
            game_address=sp.TAddress,
            new_value=sp.TNat
        ) 
    


class User(sp.Contract):
    def __init__(self,admin_address):
        self.init(
            admins = sp.set(l=[admin_address],t=sp.TAddress),
            users = sp.big_map(
                tkey = sp.TAddress,
                tvalue = sp.TRecord(
                    user_name = sp.TString, #Unique string for each user
                    user_level = sp.TNat,
                    user_tier = sp.TString,
                    user_xp = sp.TNat,
                    user_badges = sp.TList(sp.TString), #List of NFT IDs
                    profile_picture = sp.TString,
                    games_played = sp.TSet(t = sp.TAddress)
                )
            ),
            proxy_contract_address = sp.address("tz1proxy")
        )

# ################################ ADD NEW ADMIN ####################################            
    @sp.entry_point
    def add_admin(self,params):
        sp.set_type(params.new_admin_address,sp.TAddress)

        sp.verify(self.data.admins.contains(sp.source), message = "Entrypoint called by non-admin user")
        sp.verify(self.data.admins.contains(params.new_admin_address) == False, message = "This address already has admin privileges")
        
        self.data.admins.add(params.new_admin_address)

# ################################ ADD NEW USER ####################################
    @sp.entry_point
    def add_user(self,params):
        sp.set_type(params.user_address,sp.TAddress)
        sp.set_type(params.user_name,sp.TString)
        sp.set_type(params.profile_picture,sp.TString)

        # sp.verify(sp.sender==params.user_address, message = "Only user can create his own account")
        sp.verify(self.data.users.contains(params.user_address)==False,message = "User already exists with this wallet address")
        
        self.data.users[params.user_address] = sp.record(
            user_name = params.user_name, 
            user_level = sp.nat(0),
            user_tier = "",
            user_xp = sp.nat(0),
            user_badges = sp.list(),
            profile_picture = params.profile_picture,
            games_played = sp.set()
        )

# ############################# Update Profile Picture ##############################
    @sp.entry_point
    def update_profile_picture(self,params):
        sp.set_type(params.user_address,sp.TAddress)
        sp.set_type(params.ipfs_url,sp.TString)
        
        sp.verify(self.data.users.contains(params.user_address)==True,message="User does not exist")
        sp.verify(params.user_address==sp.source,message="Entrypoint cannot be called by other users")
        
        # Update the profile_picture url with new ipfs_url
        self.data.users[params.user_address].profile_picture = params.ipfs_url

    #Assumption : The picture is already uploaded to IPFS in the backend 
    #and the url of the image is passed as paramater.

# ################################ Update Username #################################    
    @sp.entry_point
    def update_username(self,params):
        sp.set_type(params.user_address,sp.TAddress)
        sp.set_type(params.new_user_name,sp.TString)
        
        sp.verify(self.data.users.contains(params.user_address)==True,message="User does not exist")
        sp.verify(params.user_address==sp.source,message="Entrypoint cannot be called by other users")

        # Update the username
        self.data.users[params.user_address].user_name = params.new_user_name   

# ################################ Add a Badge #################################    
    @sp.entry_point
    def add_badge(self,params):
        sp.set_type(params.user_address,sp.TAddress)
        sp.set_type(params.badge_id,sp.TString)
        
        sp.verify(self.data.admins.contains(sp.source),message="Entrypoint called by non-admin user")
        
        # Push the badge id to the user_badges list.
        self.data.users[params.user_address].user_badges.push(params.badge_id)   

# ################################ Add XP ####################################            
    @sp.entry_point
    def add_xp(self,params):
        sp.set_type(params.user_address,sp.TAddress)
        sp.set_type(params.additional_xp,sp.TNat)

        sp.verify(self.data.admins.contains(sp.source), message = "Entrypoint called by non-admin user")

        self.data.users[params.user_address].user_xp += params.additional_xp


# ################################ Increment level ####################################            
    @sp.entry_point
    def incr_level(self,params):
        sp.set_type(params.user_address,sp.TAddress)

        sp.verify(self.data.admins.contains(sp.source), message = "Entrypoint called by non-admin user")

        self.data.users[params.user_address].user_level += 1

# ################################ ADD GAME TO USER ####################################            
    @sp.entry_point
    def add_game_to_user(self,params):
        sp.set_type(params.user_address,sp.TAddress)
        sp.set_type(params.game_address,sp.TAddress)
        
        sp.verify(self.data.users.contains(params.user_address))
        sp.verify(self.data.admins.contains(sp.source), message = "Entrypoint called by non-admin user")
        
        self.data.users[params.user_address].games_played.add(params.game_address)

# ################################ ADD GAME TO USER ####################################            
    @sp.entry_point
    def update_proxy_address(self,params):
        sp.set_type(params.new_proxy_address,sp.TAddress)

        sp.verify(self.data.admins.contains(sp.source),message="Entrypoint cannot be called by other users")
        
        self.data.proxy_contract_address = params.new_proxy_address

###########################################################################################################################
################################################### Game Contract ########################################################
###########################################################################################################################

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
        sp.verify(self.data.games[params.game_address].admins.contains(sp.source), message = "Source != Game Admin")

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

        sp.verify(self.data.admins.contains(sp.source), message = "Entrypoint called by non-admin user")
        sp.verify(self.data.admins.contains(params.new_admin_address) == False, message = "This address already has admin privileges")
        
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


###############################################################    game_address=sp.TAddress,############################################################
################################################### Proxy Contract ########################################################
###########################################################################################################################

class Proxy_contract(sp.Contract):
    def __init__(self,admin,gage_coin_contract_address,ingame_tkn_contract_address,display_tkn_contract_address,user_contract_address,games_contract_address):
        self.init(
            admin = admin,
            gage_coin_contract_address = gage_coin_contract_address,
            ingame_tkn_contract_address = ingame_tkn_contract_address,
            display_tkn_contract_address = display_tkn_contract_address,
            user_contract_address = user_contract_address,
            games_contract_address = games_contract_address
        )
    

    ################################ Account Management ##################################     

    @sp.entry_point
    def add_user(self,params):
        sp.set_type_expr(params,User_types.add_user_type())
        sp.verify(params.user_address == sp.source)

        user_contract = sp.contract(User_types.add_user_type(),self.data.user_contract_address,entry_point = "add_user").open_some()
        sp.transfer(
            sp.record(
                user_address = params.user_address,
                user_name = params.user_name,
                profile_picture = params.profile_picture
            ), 
            sp.mutez(0), 
            user_contract
        )
    
    @sp.entry_point
    def update_username(self,params):
        sp.set_type_expr(params,User_types.update_username_type())

        sp.verify(params.user_address == sp.source)
        user_contract = sp.contract(User_types.update_username_type(),self.data.user_contract_address,entry_point = "update_username").open_some()
        sp.transfer(
            sp.record(
                user_address = params.user_address,
                new_user_name = params.new_user_name
            ), 
            sp.mutez(0), 
            user_contract
        )
    
    @sp.entry_point
    def update_profile_picture(self,params):
        sp.set_type_expr(params,User_types.update_pp_type())

        sp.verify(params.user_address == sp.source)
        user_contract = sp.contract(User_types.update_pp_type(),self.data.user_contract_address,entry_point = "update_profile_picture").open_some()
        sp.transfer(
            sp.record(
                user_address = params.user_address,
                ipfs_url = params.ipfs_url
            ), 
            sp.mutez(0), 
            user_contract
        )
    
    @sp.entry_point
    def update_proxy_in_user_contract(self,params):
        sp.set_type(params.new_proxy_address, sp.TAddress)
        sp.verify(self.data.admin == sp.sender)
        user_contract = sp.contract(sp.TRecord(new_proxy_address = sp.TAddress),self.data.user_contract_address,entry_point = "update_proxy_address").open_some()
        sp.transfer(sp.record(new_proxy_address = params.new_proxy_address), sp.mutez(0), user_contract)
    
    @sp.entry_point
    def add_game_to_user(self,params):
        sp.set_type_expr(params,User_types.add_user_to_game())
        user_contract = sp.contract(User_types.add_user_to_game(),self.data.user_contract_address,entry_point = "add_game_to_user").open_some()
        sp.transfer(
            sp.record(
                user_address = params.user_address,
                game_address = params.game_address        
            ),sp.mutez(0), user_contract
        )
    
################################ Account Management End ##################################


################################ Game Management Start ##################################
    @sp.entry_point
    def add_game(self,params):
        sp.set_type_expr(params,Game_types.create_game_type())
        games_contract = sp.contract(Game_types.create_game_type(),self.data.games_contract_address,entry_point = "add_game").open_some()
        sp.transfer(
            sp.record(
                game_address = params.game_address,
                name = params.name,
                admin = params.admin,
                description = params.description
            ),
            sp.mutez(0), games_contract
        )
    
    ################################## Update description ####################################
    @sp.entry_point
    def update_game_description(self,params):
        sp.set_type_expr(params,Game_types.update_description_type())
        games_contract = sp.contract(Game_types.update_description_type(),self.data.games_contract_address,entry_point = "update_description").open_some()
        sp.transfer(
            sp.record(
                game_address = params.game_address,
                description = params.description
            ),
            sp.mutez(0), games_contract
        )

# ################################## Update is_active ####################################
    @sp.entry_point
    def set_game_is_active(self,params):
        sp.set_type_expr(params,Game_types.set_is_active_type())
        games_contract = sp.contract(Game_types.set_is_active_type(),self.data.games_contract_address,entry_point = "set_is_active").open_some()
        sp.transfer(
            sp.record(
                game_address = params.game_address,
                is_active = params.is_active
            ),
            sp.mutez(0), games_contract
        )
        
# ################################### ADD NEW ADMIN ####################################            
    @sp.entry_point
    def add_admin_to_a_game(self,params):
        sp.set_type_expr(params,Game_types.add_admin_to_a_game_type())
        games_contract = sp.contract(Game_types.add_admin_to_a_game_type(),self.data.games_contract_address,entry_point = "add_admin_to_a_game").open_some()
        sp.transfer(
            sp.record(
                game_address = params.game_address,
                new_admin_address = params.new_admin_address
            ),
            sp.mutez(0), games_contract
        )

#  # ################################ ADD NEW ADMIN TO CONTRACT####################################            
    @sp.entry_point
    def add_admin_to_game_contract(self,params):
        sp.set_type_expr(params,Game_types.add_admin_to_game_contract_type())
        games_contract = sp.contract(Game_types.add_admin_to_game_contract_type(),self.data.games_contract_address,entry_point = "add_admin_to_contract").open_some()
        sp.transfer(
            sp.record(
                new_admin_address = params.new_admin_address
            ),
            sp.mutez(0), games_contract
        )
        
# # ################################ update total value locked ####################################            
    @sp.entry_point
    def update_total_value_locked(self,params):
        sp.set_type_expr(params,Game_types.update_total_value_locked_type())
        games_contract = sp.contract(Game_types.update_total_value_locked_type(),self.data.games_contract_address,entry_point = "update_total_value_locked").open_some()
        sp.transfer(
            sp.record(
                game_address = params.game_address,
                new_value = params.new_value
            ),
            sp.mutez(0), games_contract
        )


# # ################################ increment number of games ####################################            
    @sp.entry_point
    def incr_number_of_games_played(self,params):
        sp.set_type(params.game_address,sp.TAddress)
        games_contract = sp.contract(sp.TRecord(game_address = sp.TAddress),self.data.games_contract_address,entry_point = "incr_number_of_games_played").open_some()
        sp.transfer(
            sp.record(
                game_address = params.game_address,
            ),
            sp.mutez(0), games_contract
        )
    
################################ Game Management End ##################################



################################ SETTERS ##################################
    
    @sp.entry_point
    def update_games_contract_address(self,params):
        sp.set_type(params.games_contract_address, sp.TAddress)
        sp.verify(sp.sender == self.data.admin,message = "Admin previleges required to update")
        self.data.games_contract_address = params.games_contract_address
    
    @sp.entry_point
    def update_gage_coin_contract_address(self,params):
        sp.set_type(params.gage_coin_contract_address, sp.TAddress)
        sp.verify(sp.sender == self.data.admin,message = "Admin previleges required to update")
        self.data.gage_coin_contract_address = params.gage_coin_contract_address

    @sp.entry_point
    def update_ingame_tkn_contract_address(self,params):
        sp.set_type(params.ingame_tkn_contract_address, sp.TAddress)
        sp.verify(sp.sender == self.data.admin,message = "Admin previleges required to update")
        self.data.ingame_tkn_contract_address = params.ingame_tkn_contract_address

    @sp.entry_point
    def update_display_tkn_contract_address(self,params):
        sp.set_type(params.display_tkn_contract_address, sp.TAddress)
        sp.verify(sp.sender == self.data.admin,message = "Admin previleges required to update")
        self.data.display_tkn_contract_address = params.display_tkn_contract_address

    @sp.entry_point
    def update_user_contract_address(self,params):
        sp.set_type(params.user_contract_address, sp.TAddress)
        sp.verify(sp.sender == self.data.admin,message = "Admin previleges required to update")
        self.data.user_contract_address = params.user_contract_address

################################ SETTERS END ##################################

@sp.add_test(name="proxy_test")
def test():
    scenario = sp.test_scenario()

    admin1 = sp.test_account("admin1")
    admin2 = sp.test_account("admin2")
    fa12_contract = sp.test_account("gamegeekcoin")
    ingame_tkn_contract = sp.test_account("ingameNFT")
    display_tkn_contract = sp.test_account("displayNFT")
    
    game1 = sp.test_account("game1")
    mark = sp.test_account("mark")
    elon = sp.test_account("elon")
    
    user_contract = User(admin1.address)
    games_contract = Game(admin1.address)
    
    scenario += user_contract
    scenario += games_contract

    proxy_contract = Proxy_contract(
        admin = admin1.address,
        gage_coin_contract_address = fa12_contract.address,
        ingame_tkn_contract_address = ingame_tkn_contract.address,
        display_tkn_contract_address = display_tkn_contract.address,
        user_contract_address = user_contract.address,
        games_contract_address = games_contract.address
    )
    
    scenario += proxy_contract

    scenario += user_contract.update_proxy_address(new_proxy_address = proxy_contract.address).run(source = admin1.address) 
        
    scenario += proxy_contract.update_proxy_in_user_contract(new_proxy_address = proxy_contract.address).run(sender = admin1.address)

    scenario += proxy_contract.add_game(
            game_address = game1.address,
            name = sp.string("Space Shooter"),
            admin = admin1.address,
            description = sp.string("Shoot! Shoot! Shoot!"),
        ).run(source = game1.address)

    scenario += proxy_contract.add_user(
            user_address = mark.address, 
            user_name = sp.string("Mark"),
            profile_picture = sp.string("ipfs://adsafndaskdlfdjfkldsl")
        ).run(source = mark.address)

    # scenario += proxy_contract.update_username(
    #         user_address = mark.address, 
    #         new_user_name = sp.string("Marker"),
    #     ).run(source = mark.address)

    # scenario += proxy_contract.update_profile_picture(
    #         user_address = mark.address, 
    #         ipfs_url = sp.string("ProfilePic"),
    #     ).run(source = mark.address)

    scenario += user_contract.add_game_to_user(
            user_address = mark.address, 
            game_address = game1.address, 
        ).run(source = admin1.address)
    
    scenario += proxy_contract.set_game_is_active(
            game_address = game1.address,
            is_active = sp.bool(True),
        ).run(source = admin1.address)

    scenario += proxy_contract.add_admin_to_a_game(
            game_address = game1.address,
            new_admin_address = admin2.address,
        ).run(source = admin1.address)

    scenario += proxy_contract.add_admin_to_game_contract(
            new_admin_address = admin2.address,
        ).run(source = admin1.address)

    scenario += proxy_contract.update_total_value_locked(
            game_address = game1.address,
            new_value = sp.nat(10),
        ).run(source = admin1.address)

    scenario += proxy_contract.incr_number_of_games_played(
            game_address = game1.address,
        ).run(source = admin1.address)
