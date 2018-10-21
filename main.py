from flask import Flask, jsonify, request
import logging
import time
import json
import os
from bc_network import (my_blockchain, my_account, my_block, my_transaction, config)
from threading import Thread
from queue import Queue


app = Flask(__name__)
logging.basicConfig(level = logging.DEBUG)
BC = my_blockchain.Blockchain()
WEBHOOK_URL = 'http://0.0.0.0:5555/api/v1/transaction/check'
queue_mine_transaction_wait = Queue()
queue_mine_transaction = Queue()

# working on the nodes/ confict nodes..
# 1 node is accepted >> annouce for the others,
# How to save data in the new node, and how to connect to the new node?
# work with sign transaction ( wallet account) DOING NOW
# allow store signed "contract", signature, userid... 

def mine():
    while True:
        count_time = 0
        logging.info('watching...')
        while count_time < 11: 
            logging.info("www")
            count_time += 1
            logging.warning(count_time)
            if count_time == 10:
                logging.info("10 seconds was over!")
                if len(list(queue_mine_transaction_wait.queue)) == 0:
                    count_time = 0
                    pass
                else:
                    config.transfer_queue(queue_mine_transaction_wait, queue_mine_transaction)
                    print('do dai cua q2 = ',len(list(queue_mine_transaction.queue)))
                    BC.add_transaction(queue_mine_transaction) 
                    count_time = 0
            time.sleep(1)
        

# create a new transaction
@app.route('/api/v1/transactions', methods=['POST'])
def new_transaction():
    _from = request.json.get('from')
    _to = request.json.get('to')
    _data = request.json.get('data')
    if _from and _to and _data:
        print(" co nhan duoc du lieu dau vao !")
        queue_mine_transaction_wait.put(_from)
        queue_mine_transaction_wait.put(_to)
        queue_mine_transaction_wait.put(_data)
        if len(list(queue_mine_transaction_wait.queue)) == 0:
            return jsonify(BC.info_current_block())
        else:
            return jsonify({'status': 'in process'})
    else:
        return jsonify({'status': 'failed'})

@app.route('/api/v1/current_block', methods=['GET'])
def get_current_block():
    data = BC.info_current_block()
    return jsonify(data)


# get all of blocks in blockchain
@app.route('/api/v1/chain', methods=['GET'])
def full_chain():
    data = BC.info_all_blocks()
    print("full block chain = ", data)
    return jsonify(data)


# register a new node. a new node need to get all the chain of BC like the first node
@app.route('/api/v1/nodes/register', methods=['POST'])
def register_nodes():
    url_node = request.get_json()
    nodes = url_node.get('nodes')
    if nodes :
        count_number_node = 0   
        count_number_added_node = 0
        for node in nodes:
            count_number_node += 1
            if BC.register_node(node):
                count_number_added_node += 1
        if count_number_added_node == count_number_node:
            result = {'status': 'New nodes have been added',
                        'total_nodes': list(BC.nodes)}
        else:
            result = {'status': 'Fail to add all of new nodes'}
    else: 
        result = {'status':'Invalid json'}
    
    return jsonify(result)


@app.route('/api/v1/nodes', methods=['GET'])
def list_nodes():
    nodes = list(BC.nodes)
    json_node = []
    for i in nodes:
        json_node.append(i)
    return jsonify({'nodes': json_node})


@app.route('/api/v1/accounts/<int:user_id>', methods=['POST'])
def create_account(user_id):
    addr, priv = my_account.create_wallet_account(user_id)
    return jsonify({
        'user_id': user_id,
        'address': addr, 
        'private_key': priv
        
    })


# the api to resolve conflict >> later
@app.route('/api/v1/nodes/resolve', methods=['GET'])
def consensus():
    replaced = BC.resolve_conflicts()
    print(' new block: ', BC.info_all_blocks())
    if replaced:
        print(' new block: ', BC.info_all_blocks())
        response = {
            'message': 'Our chain was replaced',
            'new_chain': BC.info_all_blocks()
        }
    else:
        response = {
            'message':'Our chain is authoritative',
            'chain': BC.info_all_blocks()
        }
    return jsonify(response)
    

if __name__ == "__main__":
    app.debug = True
    watch_miner = Thread(target=mine)
    watch_miner.start()
    port = int(os.environ.get("PORT", 4444))
    app.run(host='0.0.0.0', port=port)