#
# This is the library of function calls that the client will be able to use.
# It should allow for read, write, etc. (possibly locking also).
# Should handle talking to each of the servers to route the response back to the client.
#

import os
import subprocess as sp
import webbrowser
from sys import platform as _platform
import requests
import ClientCache
import FileManipAPI as file_api

DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)
LOCKING_SERVER_ADDRESS = ("127.0.0.1", 5001)


# This method opens the specified file in the Windows/Linux default system text editor
def open_file_in_text_editor(full_file_path):
    if _platform == "linux" or _platform == "linux2":
        print 'Opening with Linux system editor'
        return os.system('%s %s' % (os.getenv('EDITOR'), full_file_path))
    elif _platform == "win32" or "win64":
        print 'Opening with Windows system editor'
        return sp.Popen(['notepad.exe', full_file_path]).wait()


# This method is used to request an id for this client as part of registration with the directory service.
def request_client_id():
    while True:
        try:
            response = requests.get(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], "register_client"), json={'client_id_request': True})
            break
        except:
            # probably still waiting for directory server to start up
            pass
    client_id = response.json()['client_id']
    print 'Response to request for new client_id: {0}'.format(client_id)
    return client_id


# Create an individual cache for the specified client
def create_client_cache(client_id):
    cache = ClientCache.ClientCache()
    cache.setup_cache(client_id)
    print 'New cache for client {0} created '.format(client_id)
    return cache


# Create a new directory, if it doesn't already exist.
def mkdir(dir_to_make):
    if not os.path.exists(dir_to_make):
        os.mkdir(dir_to_make)
        print 'Created directory {0} successfully.'.format(dir_to_make)
        return True
    return False

# Creates a new, empty text file locally. Doesn't create remote copy as the file is empty.
def create_new_empty_file(file_path, file_name):
    full_file_path = file_path + "/" + file_name
    absolute_dir_path = os.path.abspath(file_path)
    print "Creating new empty text file {0}".format(file_name)
    if os.path.exists(absolute_dir_path):
        new_file = open(full_file_path, 'w+')
        new_file.close()
        return True
    else:
        while(True):
            create_new_dir = raw_input("Directory {0} doesn't exist: do you want to create it now? (enter y/n): ".format(file_path))
            if str(create_new_dir).__contains__("y"):
                mkdir(file_path)
                new_file = open(full_file_path, 'w+')
                new_file.close()
                print 'Created file {0} successfully.'.format(file_name)
                return True
            elif str(create_new_dir).__contains__("n"):
                print "Couldn't create file {0}.".format(full_file_path)
                return False
            else:
                print 'Invalid answer {0} - try again!'


# Reads the specified file from the remote copy. Requires getting the remote mapping from the directory server, and then requesting the file from the fileserver directly.
# Utilises client-side caching, and waits for write locks to be released if necessary.
def read_file(file_path, file_name, client_id, cache):
    try:
        full_file_path = file_path + "/" + file_name
        print "Client requested to read " + full_file_path
        server_address, server_id, file_id, file_version = get_file_mapping_from_directory_server(full_file_path)

        if file_id is None:
            print "{0} doesn't exist as a remote copy.".format(full_file_path)
            return
        if cache.is_entry_cached_and_up_to_date(full_file_path, file_version):
            # Don't bother going to file server to fetch contents
            cache_entry = cache.fetch_cache_entry(full_file_path)
            print 'Opening local copy to update with response contents: {0}'.format(cache_entry['file_contents'])
            with open(full_file_path, 'r+') as edit_file:
                edit_file.write(cache_entry['file_contents'])
        else:
            # request the file from this file server
            while (not acquire_lock_on_file(file_id, client_id)):
                pass
            response = requests.get(
                file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_server_id': server_id})
            file_contents = response.json()['file_contents']
            if file_contents is not None:
                print 'Opening file locally to update with response contents: {0}'.format(file_contents)
                with open(full_file_path, 'r+') as edit_file:
                    edit_file.write(file_contents)

            # Add this to the cache
            cache.add_cache_entry(full_file_path, file_contents, file_version)
        open_file_in_text_editor(full_file_path)

    except Exception as e:
        print "Exception caught in read_file method: {0}".format(str(e))


# Writes to the local and remote copies of the specified file. IF the file doesn't exist, it will be created.
# Obtains mapping from directory server if file already exists, and pushes the changes to the remote copy. If this file didn't exist as a remote copy, the changes are pushed directly by the directory server.
# Uses write-locking in order to ensure atomicity of concurrent updates to the same file.
def write_file(file_path, file_name, client_id, cache):
    try:
        full_file_path = file_path + "/" + file_name
        print "Request to write " + full_file_path

        # open file for writing
        if not os.path.exists(full_file_path):
            print 'File {0} does not exist for writing: will create a new empty file locally.'.format(full_file_path)
            create_new_empty_file(file_path, file_name)
        if not os.path.exists(full_file_path):
            print "Cannot write to file {0} as it does not exist".format(full_file_path)
            return
        open_file_in_text_editor(full_file_path)
        file_contents = open(full_file_path, 'r').read()

        server_address, server_id, file_id, file_version, new_remote_copy_created = post_request_to_directory_server_for_file_mapping(full_file_path, file_contents)
        if server_id is None:
            print "There are no file servers registered with the directory server: cannot store remotely.\n Please register at least one fileserver!"
            return

        if not new_remote_copy_created:
            # we are updating an existing file on this file server
            print 'Updating remote copy of {0} with new changes'.format(full_file_path)
            while not acquire_lock_on_file(file_id, client_id):
                pass
            # We still have to post the updates to the file server
            server_response = requests.post(file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_contents': file_contents})
            print 'Response: ' + str(server_response.json())

            # TODO fixme update file version isn't working correctly
            file_version += 1
            directory_server_response = requests.post(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], "update_file_version"), json={'file_id':file_id, 'file_version':file_version, 'file_server_id': server_id, 'file_name': full_file_path})
            if directory_server_response.json()['version_updated']:
                print 'Updated version on directory server successfully'
            else:
                print "Couldn't update the version of the remote copy as expected. Consult directory server for details."
            release_lock_on_file(file_id, client_id)
        else:
            print 'Created new remote copy of {0} on file server {1}'.format(file_path, server_id)

        cache.add_cache_entry(full_file_path, file_contents, file_version)
    except Exception as e:
        print "Exception caught in write_file method: {0}".format(e.message)


# Opens the local copy of a file in the system web browser, if it exists.
def open_file(file_path, file_name, client_id, cache):
    full_file_path = file_path + "/" + file_name
    print "Request to open " + full_file_path
    if os.path.exists(full_file_path):
        webbrowser.open(full_file_path)
    else:
        print "{0} doesn't exist".format(full_file_path)


# ---------------------------#
# ---- DIRECTORY SERVER ---- #
# ---------------------------#

# Fetches the mapping details of the requested file and details of the file-server on which it is stored. Used for read requests.
def get_file_mapping_from_directory_server(full_file_path):
    print  "Get {0} mapping from directory server".format(full_file_path)
    response = requests.get(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={'file_name': full_file_path})

    file_server_address = response.json()['file_server_address']
    file_id = response.json()['file_id']
    file_server_id = response.json()['file_server_id']
    file_version = response.json()['file_version']

    print 'Response from directory server: {0}'.format(response)

    return file_server_address, file_server_id, file_id, file_version


# Fetches the mapping details for an existing remote copy, or else creates a new mapping and provides the details if the remote copy didn't exist previously. Used for write requests.
def post_request_to_directory_server_for_file_mapping(full_file_path, file_contents):
    print "Post {0} to directory server".format(full_file_path)
    response = requests.post(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={'file_name': full_file_path, 'file_contents': file_contents})

    print "Directory server response: {0}".format(response.json())
    file_server_address = response.json()['file_server_address']
    file_server_id = response.json()['file_server_id']
    file_id = response.json()['file_id']
    file_version = response.json()['file_version']
    new_remote_copy_created = response.json()['new_remote_copy']

    return file_server_address, file_server_id, file_id, file_version, new_remote_copy_created


# ---------------------------#
# ----- LOCKING SERVER ----- #
# ---------------------------#

# Ensures that a client cannot startup until it has registered with a locking server.
def register_with_locking_server(client_id):
    print 'Sending request to register client {0} with locking server..'.format(client_id)
    while True:
        try:
            response = requests.get(
                file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], "register_new_client"),
                json={'client_id': client_id})
            break
        except:
            # probably still waiting for locking server to start up
            pass
    registered = response.json()['registered']
    if registered:
        print 'Registered with locking server.'
    else:
        print 'Client could not register with locking server'


# Allows a client to place a write-lock on a file by contacting the locking server. This lock will time out if not cleared after a certain period.
def acquire_lock_on_file(file_id, client_id):
    response = requests.put(file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], ""),
                            json={'file_id': file_id, 'client_id': client_id})
    locked = response.json()['locked']
    if not locked or locked is None:
        return False
    else:
        print "Client{0} has locked file {1}".format(client_id, file_id)
        return True

# Allows a client to clear a write-lock on a file by contacting the locking server.
def release_lock_on_file(file_id, client_id):
    response = requests.delete(file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], ""),
                               json={'file_id': file_id, 'client_id': client_id})
    locked = response.json()['locked']
    if locked is None:
        print 'The client is not registered with the locking server - cannot unlock the file!'
        return None
    elif locked is False:
        print "File {0} has been unlocked".format(file_id)
        return True
    else:
        print 'The lock could not be removed'
        return False

# Allows a client to determine whether a file is already locked by contacting the locking server.
def is_file_locked(file_id):
    response = requests.get(file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], ""),
                            json={'file_id': file_id})

    locked = response.json()['locked']
    if locked is False or locked is None:
        print "File {0} isn't locked".format(file_id)
        return False
    else:
        print "File {0} is locked".format(file_id)
        return True


