import time

class Block(object):
    def __init__(self, index, previous_hash, timestamp, data, nonce, hashvalue=''):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = hashvalue
    

GENESIS = Block(
    0, '', time.time, None, 0,
    '1'
)