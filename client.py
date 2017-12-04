from flask import jsonify, Flask, request
from flask_restful import Api, Resource, abort, reqparse
import json
from blockchain import ChainBase
import blockchain as bl
from Node import Node

app = Flask(__name__)
api = Api(app)

node = Node()
chain = node.chain

block_parser = reqparse.RequestParser()
block_parser.add_argument('hash', type=str, required=True)
block_parser.add_argument('phash', type=str, required=True)
block_parser.add_argument('proof', type=str, required=True)
block_parser.add_argument('time', type=str, required=True)
block_parser.add_argument('size', type=int, required=True)
block_parser.add_argument('transactions', type=str, required=True)

class GetBlock(Resource):
    def get(self, hash):
        if len(hash) < 64: # hash is index
            index = int(hash)
            if index >= chain.size():
                abort(404, message="Blockhash {} doesn't exist".format(hash))
            return chain.chain[index].serialize()
        if hash not in chain.map:
            abort(404, message="Blockhash {} doesn't exist".format(hash))
        return chain.map[hash].serialize()

class Block(Resource):
    def post(self):
        args = block_parser.parse_args()
        data = {'hash': args['hash'],
                'phash': args['phash'],
                'proof': args['proof'],
                'time': args['time'],
                'transactions': args['transactions']}
        b = bl.Block.deserialize(data)
        if chain.is_addable(b):
            chain.add(b)
        else:
            print "Received non appliable block, discarding"
        return b.serialize(), 201

class Chain(Resource):
    def get(self):
        return chain.serialize()

node_parser = reqparse.RequestParser()
node_parser.add_argument('nodes')

class NodeRegister(Resource):
    def get(self):
        return jsonify(node.nodes)
    def post(self):
        args = block_parser.parse_args()
        data = {'nodes' : args['nodes']}
        for node in data['nodes']:
            node.register_node(node)
        return jsonify({'num_nodes': len(node.nodes)}), 201

class Mine(Resource):
    """ Automine block"""
    def get(self):
        block = node.new_block(0, chain.last_hash())
        return block.serialize(), 200

tx_parser = reqparse.RequestParser()
tx_parser.add_argument('source', required = True)
tx_parser.add_argument('target', required = True)
tx_parser.add_argument('amount', required = True)
class Transactions(Resource):
    def post(self):
        args = tx_parser.parse_args()
        return node.new_tx(args['source'], args['target'], args['amount'])

class Resolve(Resource):
    def get(self):
        updated = node.resolve()
        return {'updated': updated, 'chain': chain.serialize()}

api.add_resource(Chain, '/chain')
api.add_resource(GetBlock, '/block/<string:hash>')
api.add_resource(Block, '/block')
api.add_resource(NodeRegister, '/nodes')
api.add_resource(Transactions, '/transactions/new')
api.add_resource(Resolve, '/resolve')

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help = "Application port")
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)
