from Crypto.PublicKey import RSA
from Crypto import Random
from eth_account import Account
from binascii import unhexlify, hexlify


def create_wallet_account(user_id):
    acct = Account.create(user_id)# password is user_id
    private_key = acct.privateKey
    return acct.address, private_key.hex()


def int_to_ascii(mess):
	return unhexlify(format(mess,"x")).decode()


def verify(mess, signature, public_key , n):
    un_signature = pow(signature, public_key, n)
    return int_to_ascii(un_signature) == mess
