import blockchain as bl

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
        max_length = len(self.chain)
        for n in neighbors:
            response = requests.get('http://{}/chain'.format(n))
            if response.status_code == 200:
                length = int(response.json()['size'])
                chain  = response.json()['blocks'].deserialize()
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain  = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, proof, phash):
        block = Block(proof, phash, *self.unconfirmed_transactions)
        self.unconfirmed_transactions = []
        self.chain.add(block)
        return block
    
    def new_tx(self, source, target, amount):
        new_data = util.pack_tx(source, target, amount)
        phash = 0
        if len(self.current_transactions) > 0:
            phash = self.current_transactions[-1].hash
        tx = Transaction(phash, new_data)
        self.current_transactions.append(tx)
        return tx
        
