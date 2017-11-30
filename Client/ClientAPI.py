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
import subprocess as sp

# Directory server started at default Flask address for ease
DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)


# opens file in windows or linux default system text editor
def open_file_in_text_editor(full_file_path):
    if _platform == "linux" or _platform == "linux2":
        print 'We are on linux'
        return os.system('%s %s' % (os.getenv('EDITOR'), full_file_path))
    elif _platform == "win32" or "win64":
        print 'We are on windows '
        return sp.Popen(['notepad.exe', full_file_path]).wait()


# download a copy of the file from the file-server
# should inform lock server of the fact that it has a copy
# TODO will need to add this file to the list of locked files
def read_file(file_path, file_name):
    print "Client requested to read " + file_path + "/" + file_name

    full_file_path = file_path + "/" + file_name
    server_address, server_id, file_id = file_api.get_file_mapping_from_directory_server(full_file_path)

    # request the file from this file server
    response = requests.get(
        file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_server_id': server_id})

    if response.json['data'] is not None: # TODO test this
        print 'Opening file locally to update with response contents'
        file_to_open = open(full_file_path, 'w')
        file_to_open.write(response.json()['data'])
        open_file_in_text_editor(full_file_path) # display file to user

    # return the data that we fetched
    return response.json()['data']


# upload a changed copy of the file
# should inform the lock server of the fact that it is updating a copy
def write_file(file_path, file_name):
    full_file_path = file_path + "/" + file_name
    print "Request to write " + full_file_path
    # open file for writing
    open_file_in_text_editor(full_file_path)
    file_contents = open(full_file_path, 'r').read()

    # TODO this should at some stage return the machine on which the file is located, and its id
    server_address, server_id, file_id, new_remote_copy_created = file_api.post_request_to_directory_server_for_file_mapping(full_file_path, file_contents)
    if new_remote_copy_created == False:
        # We still have to post the updates to the file server
        response = requests.post(file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_contents': file_contents})
        print 'Response: ' + response.json()
        return response.json()


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

# This method fetches the details of the file and server on which it is stored
def get_file_mapping_from_directory_server(full_file_oath):
    print  "Sending request to directory server for file {0}".format(full_file_path)
    response = requests.get(create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={"file_name": full_file_path})

    print 'Response from server: {0}'.format(response.json())
    file_server_address = response.json()['file_server_address']
    print 'File server address is {0}:{1}'.format(file_server_address[0], file_server_address[1])
    file_id = response.json()['file_id']
    print 'File id is {0}:{1}'.format(file_id)
    file_server_id = response.json()['file_server_id']
    print 'File server id is {0}:{1}'.format(file_server_id)

    return file_server_address, file_server_id, file_id


def post_request_to_directory_server_for_file_mapping(full_file_pathcontents_to_write):
    print "Sending request to post update to file {0} from directory server"
    response = requests.post(create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={"file_name": full_file_path, "file_contents": file_contents})

    print 'Response from server: {0}'.format(str(response.json()))
    file_server_address = response.json()['file_server_address']
    file_server_id = response.json()['file_server_id']
    file_id = response.json()['file_id']
    new_remote_copy_created = response.json()['new_remote_copy']

    return file_server_address, file_server_id, file_id, new_remote_copy_created

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

