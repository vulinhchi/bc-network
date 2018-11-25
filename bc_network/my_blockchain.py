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
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import base64

Block = my_block.Block

class Blockchain(object):
    
    def __init__(self):
        self.current_transactions = [] # list transactions of current block (before add in 'chain')
        self.blocks = [my_block.GENESIS] # list all of block in bc (chain)
        self.nodes = set()# list of all nodes in bc

        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        self.http = Flask(__name__)
        # self.http.config.from_object(self)
        self.http.route('/blocks', methods=['GET'])(self.list_blocks)
        self.http.route('/nodes', methods=['GET'])(self.list_nodes)
        self.http.route('/transactions', methods=['POST'])(self.new_transaction)
        self.http.route('/current_block', methods=['GET'])(self.get_current_block)
        self.http.route('/account/<int:user_id>', methods=['POST'])(self.create_account)
        self.http.route('/nodes/resolve', methods=['GET'])(self.consensus)
        self.http.route('/nodes/update', methods=['POST'])(self.update_block)
        self.http.route('/transactions/<string:account>', methods=['GET'])(self.get_transaction_by_account)
        self.http.route('/transaction/<string:transaction_hash>', methods=['GET'])(self.get_transaction)
        self.http.route('/join',  methods=['GET'])(self.join_in)
        self.http.route('/nodes/register',  methods=['PATCH'])(self.register_node)

        self.queue_mine_transaction_wait = Queue()
        self.queue_mine_transaction = Queue()
        self.out_node_set = set()
        
    def proof_of_work(self, block):
        block.nonce = 0
        block.hash = Block.calculate_hash(block)

        while not block.hash.startswith('00'):
            block.nonce += 1
            block.hash = Block.calculate_hash(block)
        
        return block.hash  


    def add_transaction(self, queue_mine_transaction):
        print("len q2 nhan dk = ", len(list(queue_mine_transaction.queue)) )
        number_of_transaction = 0
        number_of_transaction_success = 0
        while len(list(queue_mine_transaction.queue)) > 0:
            _from = queue_mine_transaction.get()
            _to = queue_mine_transaction.get()
            _time = str(datetime.now())
            _data = queue_mine_transaction.get()
            number_of_transaction += 1
            print("new len  = ", len(list(queue_mine_transaction.queue)))
            
            # verify transaction: check signature, mess, publickey
            pub = _data['public_key']
            signature = _data['signature']
            content = _data['text']
            print(" dât = ", _data)
            pub_import = RSA.importKey(pub.encode())
            h = SHA.new(content.encode())
            
            # chuyen signature tu bytes >> string
            
            sign1 = signature.encode() # bytes
            signatue_ = base64.b64decode(sign1)
            
            verifier = PKCS1_v1_5.new(pub_import)
            result = verifier.verify(h, signatue_)
            print("ket qua: ", result)
            if result == True:
                number_of_transaction_success += 1
                items = str(_from)+ str(_to) + str(_data) + _time
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
        if number_of_transaction_success != 0:
            return self.add_block()
        else:
            print("K co transaction hop le!")
            

    def add_block(self):
        previous_block = self.blocks[-1]
        
        current_block = Block.from_previous(previous_block,"ahihi" )
        current_block.hash = self.proof_of_work(current_block)

        current_block.transactions = self.current_transactions
        print("current_block.transactions  = ", current_block.transactions )
        # add new block on the chain
        if previous_block.hash == current_block.previous_hash and current_block.index > previous_block.index:
            self.current_transactions = []
            self.blocks.append(current_block)
            print(current_block.hash)
            print("current_block.proof-of-work = ", current_block.nonce)
            return True
        else:
            return False

    def register_node(self):
        nodes = request.json.get('nodes')
        out_node = request.json.get('out_nodes')
        # print("node ahihi = ", nodes)
        # print("out_nodes ahihi = ", out_node)
        if nodes:
            for url_node in nodes:
                if url_node not in self.nodes:
                    # print("add node:", url_node)
                    parsed_url = urlparse(url_node)
                    if parsed_url.netloc and parsed_url.scheme:
                        self.nodes.add(parsed_url.netloc) 
                    elif parsed_url.path:
                        self.nodes.add(parsed_url.path)
            print("register: ", self.nodes)
        if out_node:
            for url_node in out_node:
                print("out node:", url_node)
                if url_node in self.nodes:
                    parsed_url = urlparse(url_node)
                    if parsed_url.netloc and parsed_url.scheme:
                        self.nodes.remove(parsed_url.netloc) 
                    elif parsed_url.path:
                        self.nodes.remove(parsed_url.path)
        
        return jsonify("added")


    def resolve_conflicts(self):
        nodes = self.nodes
        new_chain = None
        max_length = len(self.blocks) # count number of block, not include transaction in block
        print(nodes)
        print("max length = ", max_length )
        if not nodes: # set() is empty
            return True
        else:
            for i  in range(2200,2210):
                # print("node = ", node)
                response = requests.get(f'http://172.30.0.1:{i}/blocks')

                if response.status_code == 200:
                    chain = response.json()
                    print('DO DAI TRONG NODE ',i , " la ",len(chain))
                    if len(chain) > max_length:
                        max_length= len(chain)
                        new_chain = chain
                        
            if new_chain:
                print("new chain = ", new_chain)
                for i in new_chain:
                    for old in self.blocks:
                        if i['index'] != old.index:
                            block_item = Block(
                                i['index'],
                                i['previous_hash'],
                                i['timestamp'], 
                                i['proof-of-work'], 
                                i['transactions'], 
                                i['hash'])
                            self.blocks.append(block_item)
                
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
        all_block = []
        for block_item in self.blocks:
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
            time.sleep(1)
            for i in range(2200, 2206):
                # print(" i ai = ", i)
                try:
                    r = requests.get(f'http://172.30.0.1:{i}/join')
                    url_node = r.url
                    parsed_url = urlparse(url_node)
                    # print("self.nodes = ", self.nodes)
                    if parsed_url.netloc and parsed_url.scheme and parsed_url.netloc not in self.nodes:
                        self.nodes.add(parsed_url.netloc) 
                        # print("sau khi add self.nodes:", self.nodes)
                        
                        for u in self.nodes:
                            try:
                                nodes = list(self.nodes)
                                data = {'nodes': nodes, 'out_nodes': list(self.out_node_set)}
                                # print("data = ", data)
                                re = requests.patch(f'http://{u}/nodes/register', data=json.dumps(data), headers=config.headers)
                                print("re = ", re.url, "  -----  ", re.text)
                            
                            except:
                                # print(" U sai: ", u)
                                self.out_node_set.add(u)
                                # print(self.out_node_set)
                                pass
                    elif parsed_url.netloc in self.nodes:
                        for u in self.nodes:
                            try:
                                nodes = list(self.nodes)
                                data = {'nodes': nodes, 'out_nodes': list(self.out_node_set)}
                                # print("OUT DATA = ", data)
                                re = requests.patch(f'http://{u}/nodes/register', data=json.dumps(data), headers=config.headers)
                                # print("RE = ", re.url, "  -----  ", re.text)
                            
                            except:
                                # print(" U saiii: ", u)
                                self.out_node_set.add(u)
                                # print(self.out_node_set)
                                pass
                    

                except:
                    pass
                if i == 2205:
                    break
                
            for i in range(2206, 2211):
                # print(" i ai = ", i)
                try:
                    r = requests.get(f'http://172.31.0.1:{i}/join')
                    url_node = r.url
                    parsed_url = urlparse(url_node)
                    # print("self.nodes = ", self.nodes)
                    if parsed_url.netloc and parsed_url.scheme and parsed_url.netloc not in self.nodes:
                        self.nodes.add(parsed_url.netloc) 
                        # print("sau khi add self.nodes:", self.nodes)
                        
                        for u in self.nodes:
                            try:
                                nodes = list(self.nodes)
                                data = {'nodes': nodes, 'out_nodes': list(self.out_node_set)}
                                # print("data = ", data)
                                re = requests.patch(f'http://{u}/nodes/register', data=json.dumps(data), headers=config.headers)
                                # print("re = ", re.url, "  -----  ", re.text)
                            
                            except:
                                # print(" U sai: ", u)
                                self.out_node_set.add(u)
                                # print(self.out_node_set)
                                pass
                    elif parsed_url.netloc in self.nodes:
                        for u in self.nodes:
                            try:
                                nodes = list(self.nodes)
                                # data = {'nodes': nodes, 'out_nodes': list(self.out_node_set)}
                                # print("OUT DATA = ", data)
                                re = requests.patch(f'http://{u}/nodes/register', data=json.dumps(data), headers=config.headers)
                                # print("RE = ", re.url, "  -----  ", re.text)
                            
                            except:
                                # print(" U saiii: ", u)
                                self.out_node_set.add(u)
                                print(self.out_node_set)
                                pass
                
                except:
                    pass
                if i == 2210:
                    break
            self.out_node_set.clear()   


    # def udp_listen(self):
    #     while True:
    #         message, remote = self.udp.recvfrom(10)
    #         address , _ = remote
    #         if message == b'hello' and address not in self.nodes:
    #             # self.nodes.add(address)
    #             logging.warning('Peer discover: %s', remote)
            
    

    def join_in(self):
        return jsonify("OK")
        

    def test_update(self):
        return jsonify({'status': 'ok roi do'})
    

    def mine(self):
        while True:
            count_time = 0
            logging.info('watching...')
            while count_time < 11: 
                count_time += 1
                if count_time == 10:
                    if len(list(self.queue_mine_transaction_wait.queue)) == 0:
                        count_time = 0
                        pass
                    else:
                        config.transfer_queue(self.queue_mine_transaction_wait, self.queue_mine_transaction)
                        print('do dai cua q2 = ',len(list(self.queue_mine_transaction.queue)))
                        self.add_transaction(self.queue_mine_transaction) 
                        
                        current_block = self.blocks[-1]
                        
            # auto update new mined block to other nodes
                        block_json = {
                            'index' : current_block.index,
                            'previous_hash' : current_block.previous_hash,
                            'timestamp' : current_block.timestamp,
                            'proof-of-work' : current_block.nonce,
                            'transactions' : current_block.transactions,
                            'hash' : current_block.hash
                        
                        }
                        print("before send new block to broadcast: ")
                        # self.udp.sendto(block_string.encode(), ("255.255.255.255", 5555))
                        for i in range(2200, 2210):
                            try:
                                r = requests.post(f'http://172.30.0.1:{i}/nodes/update', data=json.dumps(block_json), headers=config.headers)
                                logging.warning('ket qua sau khi update')
                                logging.warning(r.text)
                            except:
                                pass
                        count_time = 0
                time.sleep(1)
   
   
    # API
    def list_blocks(self):
        data = self.info_all_blocks()
        return jsonify(data)

    
    def list_nodes(self):
        nodes = list(self.nodes)
        return jsonify({'nodes': nodes})

    
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
                return jsonify('successful')
        else:
            return jsonify('failed')


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


    def update_block(self):
        new_block = Block(
            request.json.get('index'),
            request.json.get('previous_hash'),
            request.json.get('timestamp'), 
            request.json.get('proof-of-work'), 
            request.json.get('transactions'), 
            request.json.get('hash'))
        print("index of new block")
        print(new_block.index)
        current_block  = self.blocks[-1]
        logging.info("new_block.hash = ")
        logging.info(new_block.previous_hash)
        logging.info("current_block.hash")
        logging.info(current_block.hash)
        if new_block.previous_hash == current_block.hash and current_block.index == new_block.index - 1: 
            self.blocks.append(new_block)
            result = {
                'status': ' successful update chain',
                # 'new_block': request.get_json()

            }
        else:
            result = {
                'status': 'failed to update chain',
                # 'new_block': request.get_json()
            }
        return jsonify(result)           


    def get_transaction_by_account(self, account):
        result = []
        for i in self.blocks:
            for j in i.transactions:
                if j['from'] == account:
                    result.append(j)
        return jsonify({'result':result})


    def get_transaction(self, transaction_hash):
        result = []
        for i in self.blocks:
            for j in i.transactions:
                if j['transaction_hash'] == transaction_hash:
                    result = j
        return jsonify({'result': result})
        

    def run(self, host='0.0.0.0'):
        logging.info('Starting...')
        self.udp.bind((host, 5555))
        watch_miner = Thread(target=self.mine)
        watch_miner.start()
        
        # udp_listen = Thread(target=self.join_in)
        udp_broadcast = Thread(target=self.udp_broadcast)

        udp_broadcast.start()
        # udp_listen.start()
        self.http.run(host=host, port = 4444)
        # udp_broadcast.join()
        # udp_listen.join()
