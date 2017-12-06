from Crypto import Random
from Crypto.PublicKey import RSA
from binascii import hexlify, unhexlify

random_gen = Random.new().read
key = RSA.generate(1024, random_gen)
encoded_key = hexlify(key.publickey().exportKey('DER'))
msg = "foobar"
emsg  = RSA.importKey(unhexlify(encoded_key)).encrypt(msg, 'x')[0]
print hexlify(emsg)
dmsg = key.decrypt(emsg)
print dmsg



