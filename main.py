from flask import Flask, jsonify, request
import logging
import time
import json
import my_transaction
import my_blockchain 
import my_account
from threading import Thread
from queue import Queue
import config


app = Flask(__name__)
logging.basicConfig(level = logging.DEBUG)
BC = my_blockchain.Blockchain()
WEBHOOK_URL = 'http://0.0.0.0:5555/api/v1/transaction/check'
queue_mine_transaction_wait = Queue()
queue_mine_transaction = Queue()

# working on the nodes/ confict nodes..
# 1 node is accepted >> annouce for the others,
# How to save data in the new node, and how to connect to the new node?
# work with sign transaction ( wallet account)
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
                if len(list(queue_mine_transaction_wait.queue)) == 0:
                    count_time == 0
                    pass
                else:
                    config.transfer_queue(queue_mine_transaction_wait, queue_mine_transaction)
                    print('do dai cua q2 = ',len(list(queue_mine_transaction.queue)))
                    BC.add_transaction(queue_mine_transaction) 
                    count_time = 0
            time.sleep(1)
        # time.sleep(1)


# create a new transaction
@app.route('/api/v1/transactions', methods=['POST'])
def new_transaction():
    _from = request.json.get('from')
    _to = request.json.get('to')
    _amount = request.json.get('amount')
    if _from and _to and _amount:
        print(" co nhan duoc du lieu dau vao !")
        queue_mine_transaction_wait.put(_from)
        queue_mine_transaction_wait.put(_to)
        queue_mine_transaction_wait.put(_amount)
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
    

    # save all info in a node
    #have to create and run a another server as a node, and check
    # can use with docker?

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
    pass

    

if __name__ == "__main__":
    app.debug = True
    watch_miner = Thread(target=mine)
    watch_miner.start()
    app.run(host='0.0.0.0', port=4444)