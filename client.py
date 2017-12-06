from flask import jsonify, Flask, request
from flask_restful import Api, Resource, abort, reqparse
import json
from blockchain import ChainBase
import blockchain as bl
from Node import Node

app = Flask(__name__)
api = Api(app)


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
            if index >= node.chain.size():
                abort(404, message="Blockhash {} doesn't exist".format(hash))
            return node.chain.chain[index].serialize()
        if hash not in node.chain.map:
            abort(404, message="Blockhash {} doesn't exist".format(hash))
        return node.chain.map[hash].serialize()

class Block(Resource):
    def post(self):
        args = block_parser.parse_args()
        data = {'hash': args['hash'],
                'phash': args['phash'],
                'proof': args['proof'],
                'time': args['time'],
                'transactions': args['transactions']}
        b = bl.Block.deserialize(data)
        if node.chain.is_addable(b):
            node.chain.add(b)
        else:
            print "Received non appliable block, discarding"
        return b.serialize(), 201

class Chain(Resource):
    def get(self):
        return node.chain.serialize()

node_parser = reqparse.RequestParser()
node_parser.add_argument('nodes', required = True)

class NodeRegister(Resource):
    def get(self):
        return list(node.nodes)

    def post(self):
        args = node_parser.parse_args()
        node.register_node(args['nodes'])
        return {'num_nodes': len(node.nodes)}, 201

class Mine(Resource):
    """ Automine block"""
    def get(self):
        block = node.new_block(0, node.chain.last_hash())
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
        return {'updated': updated, 'chain': node.chain.serialize_short()}

ns_parser = reqparse.RequestParser()
ns_parser.add_argument('source')
ns_parser.add_argument('hidden_target')
ns_parser.add_argument('server_addr')
class NewShuffler(Resource):
    def post(self):
        args = ns_parser.parse_args()
        node.new_coin_shuffle(args['source'], args['hidden_target'],
                              args['server_addr'])
        return {}, 201

shuffle_parser = reqparse.RequestParser()
shuffle_parser.add_argument('data')
class Shuffler(Resource):
    def post(self):
        args = shuffle_parser.parse_args()
        node.coin_shuffler.perform_shuffle(args['data'])
        return {}, 202

ss_parser = reqparse.RequestParser()
ss_parser.add_argument('peers')
ss_parser.add_argument('order')
ss_parser.add_argument('participants')
class StartShuffler(Resource):
    def post(self):
        args = ss_parser.parse_args()
        node.coin_shuffler.start(json.loads(args['peers']), json.loads(args['order']))

api.add_resource(Chain, '/chain')
api.add_resource(GetBlock, '/block/<string:hash>')
api.add_resource(Block, '/block')
api.add_resource(NodeRegister, '/nodes')
api.add_resource(Transactions, '/transactions/new')
api.add_resource(Resolve, '/resolve')
api.add_resource(Mine, '/mine')
api.add_resource(NewShuffler, '/coinshuffle/new')
api.add_resource(Shuffler, '/coinshuffle/shuffle')
api.add_resource(StartShuffler, '/coinshuffle/initiate')

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help = "Application port")
    parser.add_argument('--peers', nargs='*', help="Peers to add")
    parser.add_argument('-c', '--coin-shuffle-address', type=str, help= "Address of coin shuffle coordinator")
    args = parser.parse_args()
    node = Node(addr = 'http://0.0.0.0:' + str(args.port) + '/', csaddr = args.coin_shuffle_address)
    if args.peers is not None:
        for peer in args.peers:
            node.register_node(peer)
    app.run(host='0.0.0.0', port=args.port)
