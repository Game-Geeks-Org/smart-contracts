import smartpy as sp

class User(sp.Contract):
    def __init__(self):
        self.init(
            admins = sp.map(tkey = sp.TAddress,tvalue=sp.TString),
            users = sp.big_map(
                tkey = sp.TAddress,
                tvalue = sp.TRecord(
                    user_name = sp.TString, #Unique string for each user
                    user_level = sp.TNat,
                    user_badges = sp.TList(sp.TString), #List of NFT IDs
                    profile_picture = sp.TString
                )
            ),
            # admins["tz1234"] = sp.string("Hello")
        )
        

# ################################ ADD NEW ADMIN ####################################            
    @sp.entry_point
    def add_admin(self,params):
        sp.set_type(params.new_admin_address,sp.TAddress)

        # Verify that this function is called only by one of the admins.
        # sp.verify((self.data.admins.contains(sp.source)) == True, message = "Entrypoint called by non-admin user")
        # Verify that the address is not one of the admins.
        # sp.verify((self.data.admins.contains(params.new_admin_address)) == False, message = "This address already has admin privileges")
        
        self.data.admins[params.new_admin_address] = sp.string("HELLO")

# ################################ ADD NEW USER ####################################
    @sp.entry_point
    def add_user(self,params):
        sp.set_type(params.user_address,sp.TAddress)
        sp.set_type(params.user_name,sp.TString)
        sp.set_type(params.profile_picture,sp.TString)

        # Verify that this function is called only by one of the admins.
        sp.verify(self.data.admins.contains(sp.source) == True, message = "Entrypoint called by non-admin user")
        # Verify that the address is not already used by different user.
        sp.verify(self.data.users.contains(params.user_address)==False)
        
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
        
        # Check if the user ID provided actually exists in our database
        sp.verify(self.data.users.contains(params.user_address)==True)
        
        # Update the profile_picture url with new ipfs_url
        self.data.users[params.user_address].profile_picture = params.ipfs_url

    #Assumption : The picture is already uploaded to IPFS in the backend 
    #and the url of the image is passed as paramater.

# ################################ Update Username #################################    
    @sp.entry_point
    def update_username(self,params):
        sp.set_type(params.user_address,sp.TAddress)
        sp.set_type(params.user_name,sp.TString)
        
        # Check if the user ID provided actually exists in our database
        sp.verify(self.data.users.contains(params.user_address)==True)
        
        # Update the username
        self.data.users[params.user_address].user_name = params.user_name    
    
        



@sp.add_test(name="user_test1")
def test():
    scenario = sp.test_scenario()
    user_contract = User()
    scenario += user_contract
    scenario += user_contract.add_user(user_address=sp.address("tz21223141231412314"),user_name = sp.string("User_1"), profile_picture = sp.string("https://ipfs.com/xvSDfdcD/aMasdSDdcxdSDFssdaXds"))
    

