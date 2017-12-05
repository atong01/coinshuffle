import json
from Crypto import Random
from Crypto.PublicKey import RSA
from binascii import hexlify, unhexlify
def pack_tx(source, target, amount):
    return json.dumps({'source': str(source), 'target': str(target), 'amount': str(amount)})

def unpack_tx(data):
    return json.loads(data)

def generate_keypair():
    random_gen = Random.new().read
    return RSA.generate(1024, random_gen)

def public_key(keypair):
    return hexlify(keypair.publickey().exportKey('DER'))

def encrypt(epkey, msg):
    return hexlify(RSA.importKey(unhexlify(epkey)).encrypt(msg, 'x')[0])
    
def decrypt(keypair, emsg):
    return keypair.decrypt(unhexlify(emsg))

if __name__ == "__main__":
    # Test encryption
    keypair = generate_keypair()
    pubkey = public_key(keypair)
    msg = "helloworld"
    emsg = encrypt(pubkey, msg)
    dmsg = decrypt(keypair, emsg)
    print pubkey
    print msg
    print emsg
    print dmsg

