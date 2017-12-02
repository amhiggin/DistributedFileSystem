#
# This is the library of function calls that the client will be able to use.
# It should allow for read, write, etc. (possibly locking also).
# Should handle talking to each of the servers to route the response back to the client.
#

import os, sys, flask, flask_restful, requests, json
import webbrowser
import FileManipAPI as file_api
from sys import platform as _platform
import subprocess as sp
import ClientCache as cache

# Directory server started at default Flask address for ease
DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)
LOCKING_SERVER_ADDRESS = ("127.0.0.1", 5001)


# opens file in windows or linux default system text editor
def open_file_in_text_editor(full_file_path):
    if _platform == "linux" or _platform == "linux2":
        print 'Opening with Linux system editor'
        return os.system('%s %s' % (os.getenv('EDITOR'), full_file_path))
    elif _platform == "win32" or "win64":
        print 'Opening with Windows system editor'
        return sp.Popen(['notepad.exe', full_file_path]).wait()

def decrement_timeout_and_check_value(timeout):
    timeout -=1
    if timeout == 0:
        print 'Lock waiting timed out - will try to grab the lock'
    return timeout


def request_client_id():
    response = requests.get(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], "register_client"), json={'client_id_request': True})
    client_id = response.json()['client_id']
    print 'Response to request for new client_id: {0}'.format(client_id)
    return client_id


def create_client_cache(client_id, cache_path):
    cache._init_(client_id, cache_path)


def mkdir(dir_to_make):
    if not os.path.exists(dir_to_make):
        os.mkdir(dir_to_make)
        return True
    return False


# download a copy of the file from the file-server
def read_file(file_path, file_name, client_id):
    full_file_path = file_path + "/" + file_name
    print "Client requested to read " + full_file_path
    server_address, server_id, file_id = get_file_mapping_from_directory_server(full_file_path)
    # FIXME check if file already in the cache is latest version: don't have to go over network then
    # If not in cache, then proceed to try and lock the file and download from the server

    # request the file from this file server
    timeout = 50000
    while is_file_locked(file_id) and timeout is not 0:
        timeout = decrement_timeout_and_check_value(timeout)
    response = requests.get(
        file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_server_id': server_id})
    file_contents = response.json()['file_contents']
    # FIXME: add this to the cache
    if file_contents is not None: #
        print 'Opening file locally to update with response contents: {0}'.format(file_contents)
        with open(full_file_path, 'r+') as edit_file:
            edit_file.write(file_contents)

    # display file to user
    open_file_in_text_editor(full_file_path)


# write to remote copy of file on file-server
# FIXME: overwrites the remote file
def write_file(file_path, file_name, client_id):
    full_file_path = file_path + "/" + file_name
    print "Request to write " + full_file_path

    # open file for writing
    open_file_in_text_editor(full_file_path)
    file_contents = open(full_file_path, 'r').read()

    server_address, server_id, file_id, new_remote_copy_created = post_request_to_directory_server_for_file_mapping(full_file_path, file_contents)

    if new_remote_copy_created == False:
        timeout = 5000
        while not acquire_lock_on_file(file_id, client_id) and timeout is not 0:
            timeout = decrement_timeout_and_check_value(timeout)
        print 'A new remote copy was not created for this file {0}: have to push the changes directly'.format(full_file_path)
        # We still have to post the updates to the file server
        response = requests.post(file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_contents': file_contents})
        print 'Response: ' + str(response.json())
        release_lock_on_file(file_id, client_id)


# check the file exists on the file-server, as such
# TODO implement
def open_file(file_path, file_name, client_id):
    full_file_path = file_path + "/" + file_name
    print "Request to open " + full_file_path
    absolute_path = os.path.abspath(full_file_path)
    webbrowser.open(absolute_path)


# TODO implement
# doesn't really do anything effective (from what I can see)
def close_file(file_path, file_name, client_id):
    print "Request to close " + file_path + "/" + file_name


# ---------------------------#
# ---- DIRECTORY SERVER ---- #
# ---------------------------#

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


# ---------------------------#
# ----- LOCKING SERVER ----- #
# ---------------------------#

def acquire_lock_on_file(file_id, client_id):
    print "Attempting to acquire lock on file {0} for client {1}".format(file_id, client_id)
    response = requests.put(file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], ""),
                             json={'file_id': file_id, 'client_id': client_id})

    locked = response.json()['lock']
    if not locked:
        print "We didn't lock File {0} successfully".format(file_id)
        return False
    print "We have locked file {0}".format(file_id)
    return True


def release_lock_on_file(file_id, client_id):
    print "Attempting to release lock on file {0} for client {1}".format(file_id, client_id)

    response = requests.delete(file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], ""),
                             json={'file_id': file_id, 'client_id': client_id})
    locked = response.json()['lock']
    if not locked:
        print "File {0} is now unlocked".format(file_id)
        return True
    print "Couldn't unlock file {0}".format(file_id)
    return False


def is_file_locked(file_id):
    print "Checking whether the file {0} is locked".format(file_id)
    response = requests.get(file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], ""),
                               json={'file_id': file_id})

    locked = response.json()['locked']
    if not locked:
        print "File {0} isn't locked".format(file_id)
        return False
    else:
        print "File {0} is already locked".format(file_id)
        return True


