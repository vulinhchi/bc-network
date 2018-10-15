from flask import Flask, jsonify, request
import logging
import time
import my_blockchain

app = Flask(__name__)
logging.basicConfig(level = logging.DEBUG)

@app.route('/api/v1/mine', methods=['GET'])
def mine():
    pass


# create a new transaction FOCUS
@app.route('/api/v1/transactions/create', methods=['POST'])
def new_transaction():
    pass


# get all of blocks in blockchain
@app.route('/api/v1/chain', methods=['GET'])
def full_chain():
    pass


# register a new node. a new node need to get all the chain of BC like the first node
@app.route('/api/v1/nodes/register', method=['POST'])
def register_nodes():
    pass
    # get json to add node.
    # save all info in a node
    # list info of a new node


# the api to resolve conflict
@app.route('/api/v1/nodes/resolve', methods=['GET'])
def consensus():
    pass

    

if __name == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=4444)