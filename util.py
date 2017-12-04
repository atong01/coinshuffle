import json
def pack_tx(source, target, amount):
    return json.dumps({'source': source, 'target': target, 'amount': amount})

def unpack_tx(data):
    return json.loads(data)
