#
# This is the library of function calls that the client will be able to use.
# It should allow for read, write, etc. (possibly locking also).
# Should handle talking to each of the servers to route the response back to the client.
#

import os, sys
import flask
import flask_restful
import requests
import json
import FileManipAPI as file_api
from sys import platform as _platform

# Directory server started at default Flask address for ease
DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)


# opens file in windows or linux default system text editor
def open_file_in_text_editor(full_file_path):
    if _platform == "linux" or _platform == "linux2":
        os.system('%s %s' % (os.getenv('EDITOR'), full_file_path))
    elif _platform == "win32" or "win64":
        os.system("start " + full_file_path)


# download a copy of the file from the file-server
# should inform lock server of the fact that it has a copy
# TODO will need to add this file to the list of locked files
def read_file(file_path, file_name):
    print "Client requested to read " + file_path + "/" + file_name

    full_file_path = file_path + "/" + file_name
    server_address, server_id, file_id = file_api.get_file_mapping_from_directory_server(file_path, file_name)

    # request the file from this file server
    response = requests.get(
        file_api.create_url(server_address[0], server_address[1]), params={'file_id': file_id, 'file_server_id': server_id})

    if response is not None: # TODO test this
        print 'Opening file locally to update with response contents'
        file_to_open = open(full_file_path, 'w')
        file_to_open.write(response.json())
        open_file_in_text_editor(full_file_path)

    # return the data that we fetched
    return response.json()['data']


# upload a changed copy of the file
# should inform the lock server of the fact that it is updating a copy
def write_file(file_path, file_name):
    full_file_path = file_path + "/" + file_name
    print "Request to write " + full_file_path
    # open file for writing
    open_file_in_text_editor(full_file_path)
    contents_to_write = open(file_name, 'r').read()

    # TODO this should at some stage return the machine on which the file is located, and its id
    server_address, server_id, file_id = file_api.get_file_mapping_from_directory_server(file_path, file_name)
    if server_address is not None:
        response = requests.post(file_api.create_url(str(server_address).split(':')[0], str(server_address).split(':')[1], ""), json={'file_id': file_name, 'data': contents_to_write})
        print 'Response: ' + response.json()
    else:
        # FIXME - this could actually handle file creation if we wanted
        print 'Could not write to {0}: file does not exist on a server'.format(full_file_path)


# TODO implement
# check the file exists on the fileserver, as such
def open_file(file_path, file_name):
    print "Request to open " + file_path + "/" + file_name
    # NOT implemented yet


# TODO implement
# doesn't really do anything effective (from what I can see)
def close_file(file_path, file_name):
    print "Request to close " + file_path + "/" + file_name
    # NOT implemented yet


# ------------------#

# placeholder lock server methods
# NOTE: assumes that we have got the mapping for the file first
def acquire_lock_on_file(file_id):
    print "In acquire lock method"
    # does a put request to the lock server


def release_lock_on_file(file_id):
    print "In release lock method"
    # does a delete request to the lock server


def check_lock_on_file(file_id):
    print "In check lock on file method"
    # does a get request to the lock server to see whether the file  is locked

