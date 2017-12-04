import unittest
import json
from blockchain import Transaction, Block, test_chain, ChainBase

class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.t0 = Transaction(0, "hello world")
        self.t1 = Transaction(self.t0.hash, "woe is me")

    def test_serialization(self):
        t1 = self.t1
        s = json.dumps(t1.serialize())
        t = Transaction.deserialize(s)
        self.assertEqual(t.hash, t1.hash)
        self.assertEqual(t.phash, t1.phash)
        self.assertEqual(t.time, t1.time)
        self.assertEqual(t.data_hash, t1.data_hash)
        self.assertEqual(t.data, t1.data)

class TestBlock(unittest.TestCase):
    def setUp(self):
        t0 = Transaction(0, "hello world")
        t1 = Transaction(t0.hash, "woe is me")
        t2 = Transaction(t1.hash, "woe is me")
        self.b0 = Block(0, 0,t0,t1)
        self.b1 = Block(0, self.b0.hash, t2)

    def test_serialize(self):
        s = json.dumps(self.b1.serialize())
        b = Block.deserialize(s)
        assert(b.equals(self.b1))

class TestChain(unittest.TestCase):
    def setUp(self):
        self.chain = test_chain()

    def test_serialize(self):
        s = json.dumps(self.chain.serialize())
        chain = ChainBase.deserialize(s)
        assert(chain.chain[0].hash == self.chain.chain[0].hash)
        assert(chain.validate())

if __name__ == "__main__":
    unittest.main()
