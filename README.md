README
======

Compiling
---------
mkvirtualenv [environment name]

pip install -r requirements.txt

You may now run any tests or create scripts of your own.

Introduction
------------
This is a test project for the coinshuffle protocol.

We build a library for a transaction based blockchain with a coinshuffle procedure.

Overview
--------
We implement a general blockchain on top of a rest API. Each client represents a blockchain node. 

Client Interface
----------------
/chain -- [GET] returns a view of the full chain

/block/<string:hash> -- [GET] returns a view of a block for a specific hash

/block -- [POST] post a new block to the client

/nodes -- [GET] gets a list of all neighboring client nodes

/nodes -- [POST] add a list of nodes to the client

/transactions/new [POST] posts a new transaction to the client

/resolve -- [GET] calls resolve on a client which triggers it to find the longest chain among its peers

/mine -- [GET] immediately mines a block with the currently uncommited transactions on the node

/coinshuffle/new -- [POST] Create a new Coinshuffle instance (needs specified shuffle server

/coinshuffle/shuffle -- [GET] perform next step of the shuffle

/coinshuffle/initiate -- [GET] start a coinshuffle round with a specified list of peers

Future Work
-----------
Verification of transactions
Separate wallet and agents
