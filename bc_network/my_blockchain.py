import hashlib
import time
from datetime import datetime
import json
import socket
import logging
from threading import Thread
from bc_network import my_block, my_transaction, my_account, config
from urllib.parse import urlparse
from queue import Queue
import requests
from flask import Flask, jsonify, request

Block = my_block.Block

class Blockchain(object):
    
    def __init__(self):
        self.current_transactions = [] # list transactions of current block (before add in 'chain')
        self.blocks = [my_block.GENESIS] # list all of block in bc (chain)
        self.nodes = set()# list of all nodes in bc

        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        self.http = Flask(__name__)
        self.http.config.from_object(self)
        self.http.route('/', methods=['GET'])(self.a)
        self.http.route('/blocks', methods=['GET'])(self.list_blocks)
        self.http.route('/nodes', methods=['GET'])(self.list_nodes)
        self.http.route('/transactions', methods=['POST'])(self.new_transaction)
        self.http.route('/current_block', methods=['GET'])(self.get_current_block)
        self.http.route('/account/<int:user_id>', methods=['POST'])(self.create_account)
        self.http.route('/node/resolve', methods=['GET'])(self.consensus)
        
        self.queue_mine_transaction_wait = Queue()
        self.queue_mine_transaction = Queue()

    
    def a(self):
        return jsonify({'a':'fdjfdjfdj'})

        
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

        # add transaction(s)
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
            self.nodes.add(parsed_url.netloc) 
            return True
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
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


    def udp_broadcast(self):
        while True:
            # logging.warning('send broadcast ')
            self.udp.sendto(b'hello', ("255.255.255.255", 5555))
            time.sleep(1)


    def udp_listen(self):
        while True:
            # logging.warning('nhan thong tin tu broadcast')
            message, remote = self.udp.recvfrom(10)
            # logging.info('message = ')
            # logging.info(message)
            # logging.info(remote)
            address , _ = remote
            if message == b'hello' and address not in self.nodes:
                self.nodes.add(address)
                logging.warning('Peer discover: %s', remote)


    def mine(self):
        while True:
            # peer discoverd:
            count_time = 0
            logging.info('watching...')
            while count_time < 11: 
                count_time += 1
                # logging.warning(count_time)
                if count_time == 10:
                    logging.info("10 seconds was over!")
                    if len(list(self.queue_mine_transaction_wait.queue)) == 0:
                        count_time = 0
                        pass
                    else:
                        config.transfer_queue(self.queue_mine_transaction_wait, self.queue_mine_transaction)
                        print('do dai cua q2 = ',len(list(self.queue_mine_transaction.queue)))
                        self.add_transaction(self.queue_mine_transaction) 
                        count_time = 0
                time.sleep(1)
   
   
    # API
    def list_blocks(self):
        data = self.info_all_blocks()
        print("full block chain = ", data)
        return jsonify(data)

    
    def list_nodes(self):
        nodes = list(self.nodes)
        json_node = []
        for i in nodes:
            json_node.append(i)
        return jsonify({'nodes': json_node})

    
    def new_transaction(self):
        _from = request.json.get('from')
        _to = request.json.get('to')
        _data = request.json.get('data')
        if _from and _to and _data:
            print(" co nhan duoc du lieu dau vao !")
            self.queue_mine_transaction_wait.put(_from)
            self.queue_mine_transaction_wait.put(_to)
            self.queue_mine_transaction_wait.put(_data)
            if len(list(self.queue_mine_transaction_wait.queue)) == 0:
                return jsonify(self.info_current_block())
            else:
                return jsonify({'status': 'in process'})
        else:
            return jsonify({'status': 'failed'})


    def get_current_block(self):
        data = self.info_current_block()
        return jsonify(data)

    

    def create_account(self, user_id):
        addr, priv = my_account.create_wallet_account(user_id)
        return jsonify({
            'user_id': user_id,
            'address': addr, 
            'private_key': priv
            
        })

    
    def consensus(self):
        replaced = self.resolve_conflicts()
        print(' new block: ', self.info_all_blocks())
        if replaced:
            print(' new block: ', self.info_all_blocks())
            response = {
                'message': 'Our chain was replaced',
                'new_chain': self.info_all_blocks()
            }
        else:
            response = {
                'message':'Our chain is authoritative',
                'chain': self.info_all_blocks()
            }
        return jsonify(response)


    def run(self, host='0.0.0.0'):
        logging.info('Starting...')
        self.udp.bind((host, 5555))
        # watch_miner = Thread(target=self.mine)
        # watch_miner.start()
        
        udp_listen = Thread(target=self.udp_listen)
        udp_broadcast = Thread(target=self.udp_broadcast)

        udp_broadcast.start()
        udp_listen.start()
        self.http.run(host=host, port = 4444)
        udp_broadcast.join()
        udp_listen.join()
