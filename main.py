from flask import Flask, jsonify, request
import logging
import time
import json
import my_transaction
import my_blockchain 
from threading import Thread
from queue import Queue


app = Flask(__name__)
logging.basicConfig(level = logging.DEBUG)
BC = my_blockchain.Blockchain()
queue_mine_transaction_wait = Queue()
queue_mine_transaction = Queue()


def mine():
    count_time = 0
    while True:
        count_time += 1
        logging.info('watching... ')
        while len(list(queue_mine_transaction_wait.queue)) < 7 and count_time == 3: 
            logging.info("watchin mining...")
            BC.add_transaction(queue_mine_transaction_wait)
            time.sleep(3) # sleep 3s to calculate block
        time.sleep(1)


# create a new transaction FOCUS
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
    pass
    # get json to add node.
    # save all info in a node
    # list info of a new node


# the api to resolve conflict
@app.route('/api/v1/nodes/resolve', methods=['GET'])
def consensus():
    pass

    

if __name__ == "__main__":
    app.debug = True
    watch_miner = Thread(target=mine)
    watch_miner.start()
    app.run(host='0.0.0.0', port=4444)