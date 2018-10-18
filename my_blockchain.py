import hashlib
import time
from datetime import datetime
import json
import my_block, my_transaction
from urllib.parse import urlparse
from queue import Queue
import requests

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


    def add_transaction(self, queue_mine_transaction_wait):
        print('ahihihi')
        print("len q2 nhan dk = ", len(list(queue_mine_transaction_wait.queue)) )
        while len(list(queue_mine_transaction_wait.queue)) > 0:
            _from = queue_mine_transaction_wait.get()
            _to = queue_mine_transaction_wait.get()
            _amount = queue_mine_transaction_wait.get()
            _time = datetime.now()
            print("_from = ", _from)
            print("_to = ", _to)
            print("_amount = ", _amount)
            print("len q2 after get....", len(list(queue_mine_transaction_wait.queue)) )
            items = str(_from)+ str(_to) + str(_amount) + str(_time)
            items = items.encode()
            tx = {
                'sender': _from,
                'recipient': _to,
                'amount': _amount,
                'transaction_hash': hashlib.sha256(items).hexdigest(),
                'time': _time
            }
            print(tx)
            self.current_transactions.append(tx)
            print("current .. = ", self.current_transactions)
        return self.add_block()
    

    def add_block(self):
        previous_block = self.blocks[-1]
        
        current_block = Block.from_previous(previous_block,"ahihi" )
        current_block.hash = self.proof_of_work(current_block)

        # add transactions(s)
        print(" ham addblock , self.current_transactions = ",  self.current_transactions)
        current_block.transactions = self.current_transactions
        print("current_block.transactions  = ", current_block.transactions )
        # add new block on the chain
        if previous_block.hash == current_block.previous_hash and current_block.index > previous_block.index:
            self.current_transactions = []
            self.blocks.append(current_block)
            print(current_block.hash)
            print("current_block.proof-of-work = ", current_block.nonce)
            print("current block . transaction = ", current_block.transactions)
            return True
        else:
            return False

    def register_node(self, url_node):
        parsed_url = urlparse(url_node)
        if parsed_url.netloc and parsed_url.scheme:
            self.nodes.add(parsed_url.netloc) # like: http://0.0.0.0:3333
            return True
        elif parsed_url.path:
            self.nodes.add(parsed_url.path) # like: /api/v1/.... or facebook.com
            return True
        else:
            return False # invalid URL


    def resolve_conflicts(self):
        nodes = self.nodes
        new_chain = None
        max_length = len(self.blocks) # count number of block, not include transaction in block

        for node in nodes:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length:
                    max_length= length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
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

