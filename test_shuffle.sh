#!/bin/bash
c=http://0.0.0.0:500
c0=${c}0
c1=${c}1
c2=${c}2
c3=${c}3
s4=${c}4

python client.py -p 5000 --peers $c1 $c2 &
python client.py -p 5001 --peers $c0 $c2 &
python shuffle_server.py -p 5004 &
sleep 5

echo $c0/coinshuffle/new
curl -d '{"source":"alice","hidden_target":"AlicePrime","server_addr": "http://0.0.0.0:5004"}' \
   -H "Content-Type: application/json" -X POST \
   $c0/coinshuffle/new
curl -d '{"source":"bob","hidden_target":"BobPrime","server_addr": "http://0.0.0.0:5004"}' \
   -H "Content-Type: application/json" -X POST \
   $c1/coinshuffle/new
curl $s4/coinshuffle/start
curl $c1/mine
curl $c1/chain | python -m json.tool
   
sleep 3
./kill.sh
