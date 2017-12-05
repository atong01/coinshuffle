import numpy as np
from Crypto import Random
from Crypto.PublicKey import RSA
import Crypto
import util
class CoinShuffleServer:
    def __init__(self):
        self.keys = []
        self.peers = []
        self.started = False

    def submit_public_key(self, ek, address):
        keys.append(ek)
        peers.append(address)

    def get_keys(self):
        return keys

    def start(self):
        """ 
        """
        if self.started: # only start at most once
            return None, False
        self.started = True
        response = {
                "peers": {ek: addr for addr, ek in zip(self.peers, self.keys)}
                "order": {i:ek     for i,ek in enumerate(self.keys)}
                "participants": len(self.keys)
        }
        return response, True

class CoinShuffleClient:
    """ CoinShuffleClient is a per wallet function.

    If order is -1 implies not in most recent shuffle

    To Test: Multiple keys per client
    """
    def __init__(self, addr, hidden_target):
        self.amount = 1
        self.addr = addr
        self.hidden_target = hidden_target
        self.keypair  = util.generate_keypair()
        self.ek = util.public_key(self.keypair)
        self.index = None
        self.peers = None
        self.order = None
        self.is_last_shuffler = None

    def submit_ek_to_server(self, server_addr):
        requests.post(addr + 'coinshuffle/submitkey', data = {'public_key' : ek, 'address' : addr})

    def start(self, peers, order):
        """ Start coinshuffle
        peers: addr --> ek
        order: index --> addr
        """
        self.peers = peers
        self.order = order
        self.index = _find_index(self, order)
        if self.index + 1 == len(order):
        self.is_last_shuffler = (self.index + 1 == len(order))
        self.encrypted_target = self._encrypt_dest()

        if self.index != 0:
            return
        
        self.perform_shuffle({})

    def next_addr(self):
        if peers is None or order is None:
            return None
        if self.is_last_shuffler:
            return None
        return peers[order[index + 1]]

    def _find_index(self, order):
        for i,ek in order.iteritems():
            if self.ek == ek:
                return i
        return -1

    def _shuffle_data(data):
        new_order = np.random.permutation(len(data))
        new_data = {}
        for i,v in data.iter_items():
            new_data[new_order[i]] = v
        return new_data.copy() # REVIEW: is copy necessary?

    def _decrypt_data(self, data):
        new_data = {}
        for i,v in data.iter_items():
            vp = v.copy()
            vp["encrypted_addr"] = 
            new_data[i] = 

    def _encrypt_dest(self):
        t = self.hidden_target

    def perform_shuffle(self, data):
        assert self.index == len(data) + 1
        data = {
            "0" : {
                "public_key": ek
                "encrypted_addr" : 
        })
