#
# This is the library of function calls that the client will be able to use.
# It should allow for read, write, etc. (possibly locking also).
#

import os, sys
import flask
import flask_restful
import requests
import FileManipAPI as FILE_API


# download a copy of the file
# should inform lock server of the fact that it has a copy
def read_file(file_path, file_name):
    print "Request to read " + file_path
    file_server, requested_file = FILE_API.find_file_if_exists(file_path, file_name)

    if file_server is not None and requested_file is not None:
        response = requests.post(FILE_API.create_url())
        requested_file = open(file_path, 'r')
        requested_file.write(response.json()['file'])
        requested_file.close()


# upload a changed copy of the file
# should inform the lock server of the fact that it is updating a copy
def write_file(file_path, file_name):
    print "Request to write " + file_path
    file_server, requested_file = FILE_API.find_file_if_exists(file_path, file_name)

    if file_server is not None and requested_file is not None:
        return 0


# check the file exists on the fileserver, as such
def open_file(file_path):
    print "Request to open " + file_path


# doesn't really do anything effective (from what I can see)
def close_file(file_path):
    print "Request to close " + file_path
