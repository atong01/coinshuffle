#!/bin/bash
c0=http://0.0.0.0:5000
python client.py -p 5000 &
sleep 3


curl -d '{"source":"alice","target":"b","amount":"500"}' \
  -H "Content-Type: application/json" -X POST \
  $c0/transactions/new

curl $c0/mine
curl $c0/chain | python -m json.tool

sleep 3

./kill.sh
