#!/bin/sh

HOST="127.0.0.1"
INITIAL_PORT=45678

for i in $( seq 2 $1 )
do
        python FileServer/FileServer.py $HOST $INITIAL_PORT &
        INITIAL_PORT=$((INITIAL_PORT+1))
done
python FileServer/FileServer.py $HOST $INITIAL_PORT
