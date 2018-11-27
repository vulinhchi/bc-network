from Crypto.PublicKey import RSA
from Crypto import Random
from eth_account import Account
import base64
from ast import literal_eval
from binascii import unhexlify, hexlify


def create_wallet_account(user_id):
    acct = Account.create(user_id)# password is user_id
    private_key = acct.privateKey
    return acct.address, private_key.hex()


def int_to_ascii(mess):
	return unhexlify(format(mess,"x")).decode()

def verify(mess, signature, pub): # pub: key get from the blockchain/DB (string)
    # convert key from string >> bytes (base64)
    pub_bytes = pub.encode()
   
    # bytes(of base64) >> bytes (like tuple)
    pub_tuple = base64.b64decode(pub_bytes)
    
    pub_pair = literal_eval(pub_tuple.decode())
    
    n = pub_pair[1] # int
    e = pub_pair[0]
    
    un_signature = pow(signature, e, n)
    return un_signature == mess