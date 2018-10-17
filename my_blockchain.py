import hashlib
from time import time
from datetime import datetime
import json
import my_block

Block = my_block.Block

class Blockchain(object):
    def __init__(self):
        self.current_transactions = [] # list transactions of current block (before add in 'chain')
        self.blocks = [my_block.Block.genesis_block()] # list all of block in bc
        self.nodes = set()# list of all nodes in bc
    

    def proof_of_work(self, block):
        block.nonce = 0
        block.hash = Block.calculate_hash(block)

        while not block.hash.startswith('00'):
            block.nonce += 1
            block.hash = Block.calculate_hash(block)
        
        return block.hash 


    def add_block(self):
        previous_block = self.blocks[-1]
        current_block = Block.from_previous(previous_block,"hell0" )
        current_block.hash = self.proof_of_work(current_block)
        if previous_block.hash == current_block.previous_hash and current_block.index > previous_block.index:
            self.blocks.append(current_block)


BC = Blockchain()

def info_current_block():
    _info_block =[]
    current_block = BC.blocks[-1]
    info_block = {
        'index': current_block.index,
        'previous_hash': current_block.previous_hash,
        'timestamp': current_block.timestamp,
        'data': current_block.data,
        'transactions': [],
        'proof-of-work': current_block.nonce,
        'hash': current_block.hash
    }
    _info_block.append(info_block)
    return _info_block


def info_all_blocks():
    all_block = []
    for block_item in BC.blocks:
        info_block = {
            'index': block_item.index,
            'previous_hash': block_item.previous_hash,
            'timestamp': block_item.timestamp,
            'data': block_item.data,
            'transactions': [],
            'proof-of-work': block_item.nonce,
            'hash': block_item.hash
        }
        all_block.append(info_block)
    return all_block

