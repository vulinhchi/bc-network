from flask import Flask, jsonify, request
import logging
import time
import json
# import my_block
import my_blockchain 


app = Flask(__name__)
logging.basicConfig(level = logging.DEBUG)


@app.route('/api/v1/mine', methods=['GET'])
def mine():# create a new block.  1 block duoc tao thanh >> add vao chain
    pass


# create a new transaction FOCUS
@app.route('/api/v1/transactions', methods=['POST'])
def new_transaction():
    pass


@app.route('/api/v1/current_block', methods=['GET'])
def get_current_block():
    data = my_blockchain.info_current_block()
    return jsonify(data)


# get all of blocks in blockchain
@app.route('/api/v1/chain', methods=['GET'])
def full_chain():
    data = my_blockchain.info_all_blocks()
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
    app.run(host='0.0.0.0', port=4444)