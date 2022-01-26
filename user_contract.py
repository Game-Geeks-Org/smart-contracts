import smartpy as sp

class User(sp.Contract):
    def __init__(self):
        self.init(
            admins = sp.list(l=[sp.address("tz1233x1")],t=sp.TAddress),
            users = sp.big_map(
                tkey = sp.TAddress,
                tvalue = sp.TRecord(
                    user_name = sp.TString, #Unique string for each user
                    user_level = sp.TNat,
                    user_badges = sp.TList(sp.TString), #List of NFT IDs
                    profile_picture = sp.TString
                )
            ),
        )
    
    ######xxxxxxx   NOT WORKING    xxxxxx############

    # Utilary Function to check if an element is present in a list
    @sp.private_lambda(with_storage="read-only")
    def contains_in_list(self,src):
        flag = sp.bool(False)
        sp.for i in self.data.admins:
            sp.if src == i:
                flag = True
        sp.result(flag)
    a
    ######xxxxxxx   NOT WORKING    xxxxxx############

# ################################ ADD NEW ADMIN ####################################            
    @sp.entry_point
    def add_admin(self,params):
        sp.set_type(params.new_admin_address,sp.TAddress)

        sp.verify(self.contains_in_list(sp.source) == True, message = "Entrypoint called by non-admin user")
        sp.verify(self.contains_in_list(params.new_admin_address) == False, message = "This address already has admin privileges")
        
        self.data.admins.push(params.new_admin_address)

# ################################ ADD NEW USER ####################################
    @sp.entry_point
    def add_user(self,params):
        sp.set_type(params.user_address,sp.TAddress)
        sp.set_type(params.user_name,sp.TString)
        sp.set_type(params.profile_picture,sp.TString)

        # sp.verify(self.contains_in_list(self.data.admins,sp.source) == True, message = "Entrypoint called by non-admin user")        
        sp.verify(self.data.users.contains(params.user_address)==False,message = "User already exists with this wallet address")
        
        self.data.users[params.user_address] = sp.record(
            user_name = params.user_name, 
            user_level = sp.nat(0),
            user_badges = sp.list(),
            profile_picture = params.profile_picture
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
        
        # Check if the user ID provided actually exists in our database
        sp.verify(self.contains_in_list(sp.source) == True,message="Entrypoint called by non-admin user")
        # sp.verify(self.contains_in_list(self.data.admins,sp.source) == False,message="Entrypoint called by non-admin user")
        
        # Push the badge id to the user_badges list.
        self.data.users[params.user_address].user_badges.push(params.badge_id)   



@sp.add_test(name="user_test1")
def test():
    scenario = sp.test_scenario()
    
    admin1 = sp.test_account("admin1")
    admin2 = sp.test_account("admin2")
    
    mark = sp.test_account("mark")
    elon = sp.test_account("elon")
    
    user_contract = User()
    scenario += user_contract
    scenario += user_contract.add_user(user_address=mark.address,user_name = sp.string("User_1"), profile_picture = sp.string("https://ipfs.com/xvSDfdcD/aMasdSDdcxdSDFssdaXds")).run(source=admin1.address)
    scenario += user_contract.update_username(user_address=mark.address,new_user_name = sp.string("User 1")).run(source=mark.address)
    scenario += user_contract.update_profile_picture(user_address=mark.address,ipfs_url = sp.string("https://ipfs.com/aaaaaa/aMasdSDdcxdSDFssdaXds")).run(source=mark.address)
    scenario += user_contract.add_badge(user_address=mark.address,badge_id = sp.string("First Blood")).run(source=admin1.address)
    scenario += user_contract.add_admin(new_admin_address=admin2.address).run(source=admin1.address)
    

