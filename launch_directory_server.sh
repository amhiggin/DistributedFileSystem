#!/bin/sh


echo "Launching directory server on 127.0.0.1:5000"

# Launch a single directory server

python DirectoryServer/DirectoryServer.py "127.0.0.1" "5000"