from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from coin_shuffle import CoinShuffleServer
import requests
import json

key_parser = reqparse.RequestParser()
key_parser.add_argument('public_key', type=str, required=True)
key_parser.add_argument('address', type=str, required=True)
server = CoinShuffleServer()
class Keys(Resource):
    def post(self):
        args = key_parser.parse_args()
        server.submit_public_key(args['public_key'], args['address'])
        return {}, 201

class CoinShuffle(Resource):
    def get(self):
        response, dostart = server.start()
        encoded_response = {'order' : json.dumps(response['order']), 
                            'peers' : json.dumps(response['peers'])}
        if not dostart:
            abort(555, message="Coinshuffle Already Started")
        for i in range(len(response['order'])-1,-1,-1):
            ek = response['order'][i]
            addr = response['peers'][ek]
            requests.post(addr + 'coinshuffle/initiate', data = encoded_response)
        return response

class CoinShuffleReset(Resource):
    def get(self):
        server.reset()

def run():
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Keys, '/coinshuffle/submitkey')
    api.add_resource(CoinShuffle, '/coinshuffle/start')
    api.add_resource(CoinShuffleReset, '/coinshuffle/reset')

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help = "Application port")
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)

if __name__ == '__main__':
    run()

