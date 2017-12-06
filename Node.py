import blockchain as bl
import util
import requests
from coin_shuffle import CoinShuffleClient

class Node:
    def __init__(self, addr, csaddr):
        self.chain = bl.ChainBase()
        self.addr = addr
        self.nodes = set()
        self.unconfirmed_transactions = []
        self.coin_shuffle_server_address = csaddr
        self.coin_shuffler = None

    def register_node(self, node):
        self.nodes.add(node)

    def resolve(self):
        """ Resolve chain to longest chain among neighbors.

        Returns if true if we found a longer chain
        """
        neighbors = self.nodes
        max_chain = None
        max_length = self.chain.size()
        for n in neighbors:
            response = requests.get('{}/chain'.format(n))
            if response.status_code == 200:
                length = int(response.json()['size'])
                chain  = bl.ChainBase.deserialize(response.json())
                if length > max_length and chain.validate():
                    max_length = length
                    max_chain  = chain
        if max_chain:
            self.chain = max_chain
            return True
        return False

    def new_block(self, proof, phash):
        block = bl.Block(proof, phash, *self.unconfirmed_transactions)
        self.unconfirmed_transactions = []
        self.chain.add(block)
        return block

    def new_tx_from_data(self, data):
        phash = 0
        if len(self.unconfirmed_transactions) > 0:
            phash = self.unconfirmed_transactions[-1].hash
        tx = bl.Transaction(phash, data)
        self.unconfirmed_transactions.append(tx)
        return tx.serialize()
    
    def new_tx(self, source, target, amount):
        new_data = util.pack_tx(source, target, amount)
        return self.new_tx_from_data(new_data)

    def new_multi_tx(self, ins, outs):
        new_data = util.pack_multi_tx(ins, outs)
        return self.new_tx_from_data(new_data)

    def new_coin_shuffle(self, source, hidden_target, server_addr):
        self.coin_shuffler = CoinShuffleClient(self, self.addr, source, hidden_target, server_addr)

    def initiate_shuffle(self, peers, order):
        """ Initiates the shuffle part of the coin shuffle protocol.
        Returns:
            Whether protocol was successfully started
        """
        if self.coin_shuffler is None:
            return False
        self.coin_shuffler.start(peers, order)
