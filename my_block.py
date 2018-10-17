import time
from datetime import datetime
import hashlib
import my_blockchain

class Block():
    def __init__(self, index, previous_hash, timestamp, data, nonce,transactions=[], hashvalue=''):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.transactions = transactions
        self.hash = hashvalue
    
    def calculate_hash(self):
        cal = str(self.index) + str(self.previous_hash) + str(self.timestamp) + str(self.data) + str(self.nonce)
        cal = cal.encode()
        cal_hash = hashlib.sha1(cal).hexdigest()
        # self.hash = cal_hash
        return cal_hash

    
    @staticmethod
    def from_previous(block, data):
        return Block(block.index + 1, block.hash, datetime.now(), data, 0)


    @staticmethod
    def genesis_block():
        genesis =  Block(0,'',datetime.now(), "HELLO WORLD", 0)
        genesis.hash = Block.calculate_hash(genesis)
        return genesis

GENESIS = Block.genesis_block()