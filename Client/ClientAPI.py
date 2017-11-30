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


def request_client_id():
    response = requests.get(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], "register_client"), json={'client_id_request': True})
    client_id = response.json()['client_id']
    print 'Response to request for new client_id: {0}'.format(client_id)
    return client_id


# download a copy of the file from the file-server
# should inform lock server of the fact that it has a copy
# TODO will need to add this file to the list of locked files
def read_file(file_path, file_name):
    full_file_path = file_path + "/" + file_name
    print "Client requested to read " + full_file_path
    server_address, server_id, file_id = get_file_mapping_from_directory_server(full_file_path)

    # request the file from this file server
    response = requests.get(
        file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_server_id': server_id})
    file_contents = response.json()['file_contents']
    if file_contents is not None: #
        print 'Opening file locally to update with response contents: {0}'.format(file_contents)
        with open(full_file_path, 'r+') as edit_file:
            edit_file.write(file_contents)

    # display file to user
    open_file_in_text_editor(full_file_path)


# upload a changed copy of the file
# should inform the lock server of the fact that it is updating a copy
def write_file(file_path, file_name):
    full_file_path = file_path + "/" + file_name
    print "Request to write " + full_file_path
    # open file for writing
    open_file_in_text_editor(full_file_path)
    file_contents = open(full_file_path, 'r').read()

    server_address, server_id, file_id, new_remote_copy_created = post_request_to_directory_server_for_file_mapping(full_file_path, file_contents)
    if new_remote_copy_created == False:
        print 'A new remote copy was not created for this file {0}: have to push the changes directly'.format(full_file_path)
        # We still have to post the updates to the file server
        response = requests.post(file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_contents': file_contents})
        print 'Response: ' + response.json()


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
def get_file_mapping_from_directory_server(full_file_path):
    print  "Sending request to directory server for file {0}".format(full_file_path)
    response = requests.get(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={'file_name': full_file_path})
    print 'Response from server: {0}'.format(response.json())

    file_server_address = response.json()['file_server_address']
    print 'File server address is {0}:{1}'.format(file_server_address[0], file_server_address[1])
    file_id = response.json()['file_id']
    print 'File id is {0}'.format(file_id)
    file_server_id = response.json()['file_server_id']
    print 'File server id is {0}'.format(file_server_id)

    return file_server_address, file_server_id, file_id


def post_request_to_directory_server_for_file_mapping(full_file_path, file_contents):
    print "Sending request to post update to file {0} from directory server".format(full_file_path)
    response = requests.post(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={'file_name': full_file_path, 'file_contents': file_contents})

    print 'Response from server: {0}'.format(str(response.json()))
    file_server_address = response.json()['file_server_address']
    print 'File server address: {0}{1}'.format(file_server_address[0], file_server_address[1])
    file_server_id = response.json()['file_server_id']
    print 'File server id: {0}'.format(file_server_id)
    file_id = response.json()['file_id']
    print 'File id: {0}'.format(file_id)
    new_remote_copy_created = response.json()['new_remote_copy']
    print 'New remote copy created?: {0}'.format(str(new_remote_copy_created))

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

