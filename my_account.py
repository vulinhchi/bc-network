from Crypto.PublicKey import RSA
from Crypto import Random
from eth_account import Account

def create_wallet_account(user_id):
    acct = Account.create(user_id)# password is user_id
    private_key = acct.privateKey
    return acct.address, private_key.hex()