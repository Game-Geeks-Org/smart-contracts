import smartpy as sp
FA2 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA2.py")

class GGToken(FA2.FA2):
    def __init__(self, config, metadata, admin):
        FA2.FA2.__init__(self, config, metadata, admin)
        self.update_initial_storage(
        token_holders = sp.big_map(l = {}, tkey = sp.TAddress, tvalue = sp.TNat), # 0 = None, 1 = Silver, 2 = Gold, 3 = Platinum
        )
    
    @sp.onchain_view()
    def getToken(self, user):
        sp.result(self.data.token_holders.get(user, 0))
    
    @sp.entry_point
    def mint(self, params):
        sp.verify(sp.sender == self.data.administrator, 'FA2_NOT_ADMIN')
        sp.verify(~self.data.token_holders.contains(params.address), 'User Already has this NFT')
        sp.verify(params.amount == 1, 'NFT-asset: amount <> 1')
        sp.verify(~ (params.token_id < self.data.all_tokens), 'NFT-asset: cannot mint twice same token')
        sp.if self.data.ledger.contains((sp.set_type_expr(params.address, sp.TAddress), sp.set_type_expr(params.token_id, sp.TNat))):
            self.data.ledger[(sp.set_type_expr(params.address, sp.TAddress), sp.set_type_expr(params.token_id, sp.TNat))].balance += params.amount
        sp.else:
            self.data.ledger[(sp.set_type_expr(params.address, sp.TAddress), sp.set_type_expr(params.token_id, sp.TNat))] = sp.record(balance = params.amount)
        sp.if ~ (params.token_id < self.data.all_tokens):
            sp.verify(self.data.all_tokens == params.token_id, 'Token-IDs should be consecutive')
            self.data.all_tokens = params.token_id + 1
            self.data.token_metadata[params.token_id] = sp.record(token_id = params.token_id, token_info = params.metadata)
        self.data.total_supply[params.token_id] = params.amount + self.data.total_supply.get(params.token_id, default_value = 0)
        self.data.token_holders[params.address] = params.token_type


@sp.add_test(name = "Non Fungible Token")
def test():
    scenario = sp.test_scenario()
    
    admin = sp.address("tz1LXRS2zgh12gbGix6R9xSLJwfwqM9VdpPW")
    mark = sp.test_account("user1")
    elon = sp.test_account("user2")

    token_contract = GGToken(config = FA2.FA2_config(non_fungible = True), admin = admin, metadata = sp.utils.metadata_of_url("ipfs://QmW8jPMdBmFvsSEoLWPPhaozN6jGQFxxkwuMLtVFqEy6Fb"))
    scenario += token_contract
