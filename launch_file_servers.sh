
#!/bin/sh

HOST="127.0.0.1"
INITIAL_PORT=45678

for i in $( seq 2 $1 )
do
        # kill any running process on the port
        lsof -i tcp:${INITIAL_PORT} | awk 'NR!=1 {print $2}' | xargs kill
        # start the server on the port
        python FileServer/FileServer.py $HOST $INITIAL_PORT &
        # increment the port number
        INITIAL_PORT=$((INITIAL_PORT+1))
done
python FileServer/FileServer.py $HOST $INITIAL_PORT
