import logging
import sys
from bc_network import my_blockchain


logging.basicConfig(level = logging.DEBUG)


# register a new node. a new node need to get all the chain of BC like the first node
# @app.route('/api/v1/nodes/register', methods=['POST'])
# def register_nodes():
#     url_node = request.get_json()
#     nodes = url_node.get('nodes')
#     if nodes :
#         count_number_node = 0   
#         count_number_added_node = 0
#         for node in nodes:
#             count_number_node += 1
#             if BC.register_node(node):
#                 count_number_added_node += 1
#         if count_number_added_node == count_number_node:
#             result = {'status': 'New nodes have been added',
#                         'total_nodes': list(BC.nodes)}
#         else:
#             result = {'status': 'Fail to add all of new nodes'}
#     else: 
#         result = {'status':'Invalid json'}
    
#     return jsonify(result)


if __name__ == '__main__':
    server = my_blockchain.Blockchain()
    server.run()