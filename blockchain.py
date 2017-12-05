import datetime
import hashlib
import time
import json
from util import pack_tx
hasher = hashlib.sha256
encoding = 'utf-8'
max_transaction_data_length = 1024
DEBUG = True

def now():
    return 0 if DEBUG else time.time() 

class Transaction:
    def __init__(self, phash, data):
        self.phash = phash
        self.data  = data
        self.size  = len(data.encode(encoding))
        self.time  = now()
        self.data_hash = self._hash_data()
        self.hash  = self._hash()

    def _hash_data(self):
        return hasher(bytearray(str(self.time) +
                                str(self.data), encoding)).hexdigest()

    def _hash(self):
        return hasher(bytearray(str(self.phash) + 
                                str(self.time) +
                                str(self.data_hash), encoding)).hexdigest()

    def validate(self):
        if self.data_hash != self._hash_data():
            print "ERROR: Invalid data hash in " + str(self)
            return False
        if self.hash != self._hash():
            print "ERROR: Invalid hash in " + str(self)
            return False
        return True

    def short_string(self, limit):
        hash_str = self.hash[:limit] if self.hash else None
        phash_str = self.phash[:limit] if self.phash else self.phash
        return 'Transaction<phash: {}, hash: {}, data: {}>'.format(
                phash_str, hash_str, self.data)

    def __repr__(self):
        return self.short_string(4)

    def serialize(self):
        return {'hash': self.hash,
                'phash': self.phash,
                'time' : self.time,
                'data_hash' : self.data_hash,
                'data' : self.data}

    @classmethod
    def deserialize(cls, d):
        if type(d) is not dict:
            d = json.loads(d)
        t = cls(d['phash'],d['data'])
        t.hash  = d['hash']
        t.time  = d['time']
        t.data_hash = d['data_hash']
        return t

class Block:
    def __init__(self, proof, phash, *args):
        self.proof = proof
        self.phash = phash
        self.hash  = None
        self.items = []
        self.map   = {}
        self.time  = None
        if args:
            for elem in args:
                self.add_item(elem)
        self._seal()

    def add_item(self, transaction):
        transaction.validate()
        if len(self.items) != 0 and transaction.phash != self.items[-1].hash:
            raise RuntimeException("Transaction cannot be added {}".format(transaction))
        self.items.append(transaction)
        self.map[transaction.hash] = transaction

    def _seal(self):
        self.time = now()
        self.hash = self._hash()

    def _hash(self):
        item_hash = ""
        if len(self.items) > 0:
            item_hash = str(self.items[-1].hash)
        return hasher(bytearray(str(self.phash) + 
                                str(self.proof) +
                                str(self.time)  +
                                item_hash, encoding)).hexdigest()

    def _validate_items(self):
        for i,v in enumerate(self.items):
            if not v.validate():
                print "Invalid Block transaction validation failed"
                return False
            if i > 0 and v.phash != self.items[i-1].hash:
                print "Invalid Block transaction hash in block " + str(self)
                return False
        return True

    def validate(self):
        if self.hash != self._hash():
            return False
        return self._validate_items()

    def short_string(self, limit):
        hash_str = self.hash[:limit] if self.hash else None
        phash_str = self.phash[:limit] if self.phash else self.phash
        return 'Block<phash: {}, hash: {}, proof: {}, length: {}>'.format(
                phash_str, hash_str, self.proof, len(self.items))

    def __repr__(self):
        return self.short_string(4)

    def serialize_short(self):
        return {'hash':  self.hash,
                'phash': self.phash,
                'proof': self.proof,
                'time':  self.time,
                'size':  len(self.items),
                'transactions': json.dumps({i:v.hash for i,v in enumerate(self.items)})}
    
    def serialize(self):
        return {'hash':  self.hash,
                'phash': self.phash,
                'proof': self.proof,
                'time':  self.time,
                'size':  len(self.items),
                'transactions': json.dumps({i:v.serialize() for i,v in enumerate(self.items)})}

    @classmethod
    def deserialize(cls, d):
        if type(d) is not dict:
            print type(d)
            d = json.loads(d)
        b = Block(d['proof'], d['phash'])
        b.time = d['time']
        b.hash = d['hash']
        tx_dict = json.loads(d['transactions'])
        for i in range(len(tx_dict)):
            t = tx_dict[str(i)]
            test= Transaction.deserialize(t)
            b.add_item(Transaction.deserialize(t))
        return b

    def equals(self, other):
        if not isinstance(other, Block):
            return False
        return_val = True
        return_val &= (self.time == other.time)
        return_val &= (self.hash == other.hash)
        return_val &= (self.phash == other.phash)
        return_val &= (self.proof == other.proof)
        return return_val

class ChainBase:
    def __init__(self):
        self.chain = []
        self.map   = {}
        self.add(genesis_block())

    def is_addable(self, block):
        if len(self.chain) == 0:
            return True
        return block.phash == self.chain[-1].hash

    def add(self, block):
        if not self.is_addable(block):
            raise RuntimeError("Block cannot be added with incorrect hash")
        self.chain.append(block)
        self.map[block.hash] = block

    def validate(self):
        for i,v in enumerate(self.chain):
            if not v.validate():
                return False
        return True

    def __repr__(self):
        return "ChainBase<length: {}>".format(self.size())

    def size(self):
        return len(self.chain)

    def serialize(self):
        return {'blocks' : {i:v.serialize() for i,v in enumerate(self.chain)},
                'size' : len(self.chain)}

    def serialize_short(self):
        return {'size' : len(self.chain)}

    def last_hash(self):
        to_return = 0
        if len(self.chain) > 0:
            to_return = self.chain[-1].hash
        return to_return

    @classmethod
    def deserialize(cls, d):
        if type(d) is not dict:
            d = json.loads(d)
        new_chain = ChainBase()
        for i in range(len(d['blocks'])):
            b = Block.deserialize(d['blocks'][str(i)])
            new_chain.add(b)
        return new_chain

class TransactionChain(ChainBase):
    def __init__(self):
        super(TransactionChain, self).__init__()

    def validate(self):
        if not super(TransactionChain, self).validate():
            raise RuntimeError("Chain hash validation failed")

    def _block_validate(self):
        """ Additional block level verification """




def genesis_block():
    t0 = Transaction(0,       pack_tx("0", "Alice", 100))
    t1 = Transaction(t0.hash, pack_tx("0", "Bob"  , 100))
    t2 = Transaction(t1.hash, pack_tx("0", "Cher" , 100))
    t3 = Transaction(t2.hash, pack_tx("0", "Devin", 100))
    return Block(0,0,t0,t1,t2,t3)

def test_chain():
    return ChainBase()

if __name__ == "__main__":
    chain = test_chain()
