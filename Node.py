import blockchain as bl
import util
import requests

class Node:
    def __init__(self):
        #TODO uncomment
#        self.chain = bl.ChainBase()
        self.chain = bl.test_chain()
        self.nodes = set()
        self.unconfirmed_transactions = []

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
            print "Attempting to send to " + n
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
    
    def new_tx(self, source, target, amount):
        new_data = util.pack_tx(source, target, amount)
        phash = 0
        if len(self.unconfirmed_transactions) > 0:
            phash = self.unconfirmed_transactions[-1].hash
        tx = bl.Transaction(phash, new_data)
        self.unconfirmed_transactions.append(tx)
        return tx.serialize()
        
