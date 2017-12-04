#!/bin/bash
c0=http://0.0.0.0:5000
c1=http://0.0.0.0:5001
c2=http://0.0.0.0:5002
python client.py -p 5000 --peers $c1 $c2 &
python client.py -p 5001 --peers $c0 $c2 &
python client.py -p 5002 --peers $c0 $c1 &
sleep 3

curl -d '{"source":"a","target":"b","amount":"500"}' \
  -H "Content-Type: application/json" -X POST \
  http://0.0.0.0:5002/transactions/new

curl http://0.0.0.0:5002/mine
curl http://0.0.0.0:5001/resolve
curl http://0.0.0.0:5001/chain | python -m json.tool

sleep 3

./kill.sh
