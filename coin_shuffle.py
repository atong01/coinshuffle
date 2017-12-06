import numpy as np
from Crypto import Random
from Crypto.PublicKey import RSA
import Crypto
import util
import json
import requests

class CoinShuffleServer:
    def __init__(self):
        self.keys = []
        self.peers = []
        self.started = False

    def submit_public_key(self, ek, address):
        self.keys.append(ek)
        self.peers.append(address)

    def get_keys(self):
        return keys

    def start(self):
        """ 
        """
        if self.started: # only start at most once
            return None, False
        self.started = True
        response = {
                "peers": {ek: addr for addr, ek in zip(self.peers, self.keys)},
                "order": {i:ek     for i,ek in enumerate(self.keys)},
                "participants": len(self.keys)
        }
        return response, len(self.keys) > 0

    def reset(self):
        """ Resets the coinshuffle process so we can start it again.
        """
        to_return = self.started
        self.started = False
        self.keys = []
        self.peers = []
        return to_return

class CoinShuffleClient:
    """ CoinShuffleClient is a per wallet function.

    If order is -1 implies not in most recent shuffle

    To Test: Multiple keys per client
    """
    def __init__(self, node, addr, source, hidden_target, server_addr):
        self.amount = 1
        self.addr = addr
        self.source = source
        self.hidden_target = hidden_target
        self.keypair  = util.generate_keypair()
        self.ek = util.public_key(self.keypair)
        self.index = None
        self.peers = None
        self.order = None
        self.is_last_shuffler = None
        self.server_addr = server_addr
        self.submit_ek_to_server(server_addr)
        self.node = node
        self.start_called = False

    def submit_ek_to_server(self, addr):
        requests.post(addr + '/coinshuffle/submitkey', data = {'public_key' : self.ek, 'address' : self.addr})

    def start(self, peers, order):
        """ Start coinshuffle procedure.
        peers: addr --> ek
        order: index --> addr
        """
        assert type(order) == dict
        assert type(peers) == dict
        self.start_called = True
        self.peers = peers
        self.num_peers = len(peers)
        self.order = order
        self.index = int(self._find_index(order))
        self.is_last_shuffler = (self.index + 1 == len(order))
        self.encrypted_target = self._encrypt_dest()
        if self.index != 0:
            return
        self.perform_shuffle(json.dumps({}), json.dumps({}))

    def next_addr(self):
        if self.peers is None or self.order is None:
            return None
        if self.is_last_shuffler:
            return None
        return self.peers[self.order[str(self.index + 1)]]

    def _find_index(self, order):
        for i,ek in order.iteritems():
            if self.ek == ek:
                return i
        return -1

    def _shuffle_data(self, data):
        new_order = list(np.random.permutation(len(data)))
        new_data = {}
        for i,v in data.iteritems():
            new_data[str(new_order[int(i)])] = v
        return new_data.copy() # REVIEW: is copy necessary?

    def _decrypt_data(self, data):
        new_data = {}
        for i,v in data.iteritems():
            vp = v.copy()
            vp["target"] = util.decrypt(self.keypair, v["target"])
            new_data[i] = vp
        return new_data.copy()

    def _encrypt_dest(self):
        t = self.hidden_target
        for i in range(self.num_peers-1,self.index,-1):
            t = util.encrypt(self.order[str(i)], t)
        return t

    def perform_shuffle(self, sources, data):
        print type(sources)
        sources = json.loads(sources)
        data = json.loads(data)
        assert self.index == len(data)
        data = self._decrypt_data(data)
        data[str(self.index)] = {
            "public_key": self.ek,
            "target": self.encrypted_target
        }
        sources[str(self.index)] = {"source": self.source}
        data = self._shuffle_data(data)
        if self.index == self.num_peers - 1:
            self.construct_transactions(sources, data)
        else:
            requests.post(self.next_addr() + "coinshuffle/shuffle", {'data': json.dumps(data), 'sources':json.dumps(sources)})

    def construct_transactions(self, sources, data):
        """ Construct a new transaction block.

        Use Node operations to construct a new block.
        """
        new_data = {'in':{}, 'out':{}}
        ins = {}
        outs = {}
        for i,tx in data.iteritems():
            source = sources[str(i)]
            ins[str(i)]  = {'amount' : self.amount, 'addr': source}
            outs[str(i)] = {'amount' : self.amount, 'addr': tx['target']}
        print ins, outs
        self.node.new_multi_tx(ins, outs)
