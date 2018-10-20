from bc_network import my_blockchain
import hashlib


def data_transaction(_text, _public_key, _signature, _user_id, _username):
    data_form = {
        'text': _text,
        'signature': _signature,
        'public_key': _public_key,
        'user_id': _user_id,
        'username': _username
    }
    return data_form


def create_transaction(_from, _to, _time):
    transaction_form = {
        'from': _from,
        'to': _to,
        'data': data_transaction
    }

    return transaction_form


