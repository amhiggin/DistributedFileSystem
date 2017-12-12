#!/bin/sh

echo "Launching locking server on 127.0.0.1:5001"

# Launch a single locking server

python LockingServer/LockingServer.py "127.0.0.1" "5001"