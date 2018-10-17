import hashlib
from time import time
from datetime import datetime
import json
import my_block, my_transaction

Block = my_block.Block

class Blockchain(object):
    
    def __init__(self):
        self.current_transactions = [] # list transactions of current block (before add in 'chain')
        self.blocks = [my_block.GENESIS] # list all of block in bc
        self.nodes = set()# list of all nodes in bc
    

    def proof_of_work(self, block):
        block.nonce = 0
        block.hash = Block.calculate_hash(block)

        while not block.hash.startswith('00'):
            block.nonce += 1
            block.hash = Block.calculate_hash(block)
        
        return block.hash 


    def add_transaction(self, _from, _to, _amount):
        txs = []
        items = str(_from)+ str(_to) + str(_amount)
        items = items.encode()
        tx = {
            'sender': _from,
            'recipient': _to,
            'amount': _amount,
            'transaction_hash': hashlib.sha256(items).hexdigest()
        }
        txs.append(tx)
        self.current_transactions.append(tx)
        print('txs = ', txs)
        print("add transaction: ", self.current_transactions)
        

    def add_block(self):
        print("Number of block in BC: ", len(self.blocks))
        previous_block = self.blocks[-1]
        
        current_block = Block.from_previous(previous_block,"ahihi" )
        current_block.hash = self.proof_of_work(current_block)

        # add transactions(s)
        # my_transaction.add_transaction()
        print('current_transaction in add block : ', self.current_transactions)
        current_block.transactions = self.current_transactions
        # add new block on the chain
        print("previous_block.hash = ",previous_block.hash )
        print("current_block.previous_hash = ", current_block.previous_hash)
        print("current_block.index = " , current_block.index)
        print("previous_block.index = ", previous_block.index)
        current_block_json = {
            'index': current_block.index,
            'previous_hash': current_block.previous_hash,
            'timestamp': current_block.timestamp,
            'data': current_block.data,
            'transactions': current_block.transactions,
            'proof-of-work': current_block.nonce,
            'hash': current_block.hash
        }
        print(current_block_json)
        if previous_block.hash == current_block.previous_hash and current_block.index > previous_block.index:
            self.current_transactions = []
            self.blocks.append(current_block)
            print("Number of block in BC: ", len(self.blocks))
            print("ket qua ")
            print(self.info_all_blocks())
            return True
        else:
            return False
        

    def info_current_block(self):
        _info_block =[]
        current_block = self.blocks[-1]
        info_block = {
            'index': current_block.index,
            'previous_hash': current_block.previous_hash,
            'timestamp': current_block.timestamp,
            'data': current_block.data,
            'transactions': current_block.transactions,
            'proof-of-work': current_block.nonce,
            'hash': current_block.hash
        }
        _info_block.append(info_block)
        return _info_block


    def info_all_blocks(self):
        print("Number of block in BC: ", len(self.blocks))
        all_block = []
        for block_item in self.blocks:
            info_block = {
                'index': block_item.index,
                'previous_hash': block_item.previous_hash,
                'timestamp': block_item.timestamp,
                'data': block_item.data,
                'transactions': block_item.transactions,
                'proof-of-work': block_item.nonce,
                'hash': block_item.hash
            }
            all_block.append(info_block)
        return all_block

