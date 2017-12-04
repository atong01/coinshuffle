import unittest
import client
import requests
import json
from blockchain import Block, Transaction, ChainBase, test_chain

def get_json(response):
    return json.loads(response.get_data())

class TestClient(unittest.TestCase):
    def setUp(self):
        self.app = client.app.test_client()
        self.chain = test_chain()

    def test_get_chain(self):
        response = get_json(self.app.get('chain'))
        self.assertEqual(response["blocks"]["1"]["hash"], '879e721969f6655c12f9d74c9cbecfc2dfc257df3a512e98476519956307ce9e')

    def test_get_block(self):
        response = get_json(self.app.get('block/1'))
        block = Block.deserialize(response)
        assert(block.equals(self.chain.chain[1]))

    def test_post_block(self):
        t0 = Transaction(0, "Foo")
        block = Block(0, self.chain.chain[-1].hash, t0)
        self.chain.add(block)
        response = requests.post('http://localhost:5000/block', data=block.serialize())

if __name__ == "__main__":
    unittest.main()

