#!/bin/bash
c0=http://0.0.0.0:5000
c1=http://0.0.0.0:5001
c2=http://0.0.0.0:5002
python client.py -p 5000 --peers $c1 $c2 &
python client.py -p 5001 --peers $c0 $c2 &
python client.py -p 5002 --peers $c0 $c1 &
sleep 3

curl -d '{"source":"alice","target":"b","amount":"500"}' \
  -H "Content-Type: application/json" -X POST \
  $c2/transactions/new

curl $c2/mine
curl $c1/resolve
curl $c1/chain | python -m json.tool
curl $c1/resolve
curl $c1/chain | python -m json.tool

sleep 3

./kill.sh
