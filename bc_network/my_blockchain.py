import hashlib
import time
from datetime import datetime
import json
from bc_network import my_block, my_transaction
from urllib.parse import urlparse
from queue import Queue
import requests

Block = my_block.Block

class Blockchain(object):
    
    def __init__(self):
        self.current_transactions = [] # list transactions of current block (before add in 'chain')
        self.blocks = [my_block.GENESIS] # list all of block in bc (chain)
        self.nodes = set()# list of all nodes in bc
    

    def proof_of_work(self, block):
        block.nonce = 0
        block.hash = Block.calculate_hash(block)

        while not block.hash.startswith('00'):
            block.nonce += 1
            block.hash = Block.calculate_hash(block)
        
        return block.hash  


    def add_transaction(self, queue_mine_transaction):
        print("len q2 nhan dk = ", len(list(queue_mine_transaction.queue)) )
        while len(list(queue_mine_transaction.queue)) > 0:
            _from = queue_mine_transaction.get()
            _to = queue_mine_transaction.get()
            _time = datetime.now()
            _data = queue_mine_transaction.get()
            
            items = str(_from)+ str(_to) + str(_data) + str(_time)
            items = items.encode()
            tx = {
                'from': _from,
                'to': _to,
                'data': _data,
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
        print(nodes)
        print("max length = ", max_length )
        if not nodes: # set() is empty
            return True
        else:
            for node in nodes:
                print("node = ", node)
                response = requests.get(f'http://{node}/api/v1/chain')

                if response.status_code == 200:
                    chain = response.json()
                    print('do dai trong node ',node , " la ",len(chain))
                    if len(chain) > max_length:
                        max_length= len(chain)
                        new_chain = chain
                        
            if new_chain:
                print("new chain = ", new_chain)
                for i in new_chain:
                    block_item = Block(i['index'],i['previous_hash'],i['timestamp'], i['proof-of-work'], i['transactions'], i['hash'])
                    self.blocks.append(block_item)
                
                print("self.blocks = ", self.blocks)
                return True
            return False


    def info_current_block(self):
        _info_block =[]
        current_block = self.blocks[-1]
        info_block = {
            'index': current_block.index,
            'previous_hash': current_block.previous_hash,
            'timestamp': current_block.timestamp,
            'transactions': current_block.transactions,
            'proof-of-work': current_block.nonce,
            'hash': current_block.hash
        }
        _info_block.append(info_block)
        return _info_block


    def info_all_blocks(self):
        print("Number of block in BC: ", len(self.blocks))
        print('type after set : ', type(self.blocks))
        print('dlgfkgjfjgkfgjkfff', self.blocks)
        all_block = []
        for block_item in self.blocks:
            print('type of block_item : ', type(block_item))
            print('get info in each block : ',block_item)
            info_block = {
                'index': block_item.index,
                'previous_hash': block_item.previous_hash,
                'timestamp': block_item.timestamp,
                'transactions': block_item.transactions,
                'proof-of-work': block_item.nonce,
                'hash': block_item.hash
            }
            all_block.append(info_block)
        return all_block

