#
# This is the library of function calls that the client will be able to use.
# It should allow for read, write, etc. (possibly locking also).
# Should handle talking to each of the servers to route the response back to the client.
#

import os, sys
import subprocess as sp
from sys import platform as _platform
import requests
import ClientCache
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import FileManipAPI as file_api

DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)
LOCKING_SERVER_ADDRESS = ("127.0.0.1", 5001)


# Allows the user to distinguish between the clients' output.
def print_to_console(client_id, message):
    print 'Client{0}: {1}'.format(client_id, message)


# This method opens the specified file in the Windows/Linux default system text editor, depending on the platform.
def open_file_in_text_editor(full_file_path, client_id):
    if _platform == "linux" or _platform == "linux2":
        print_to_console(client_id, 'Launching Linux system text editor')
        return os.system('%s %s' % (os.getenv('EDITOR'), full_file_path))
    elif _platform == "win32" or "win64":
        print_to_console(client_id, 'Launching Windows system text editor')
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
    print_to_console(client_id, 'Response to request for new client_id: {0}'.format(client_id))
    return client_id


# Create an individual cache for the specified client
def create_client_cache(client_id):
    cache = ClientCache.ClientCache()
    cache.setup_cache(client_id)
    print_to_console(client_id, 'New cache for client {0} created '.format(client_id))
    return cache


# Create a new directory, if it doesn't already exist.
def mkdir(dir_to_make, client_id):
    if not os.path.exists(dir_to_make):
        os.mkdir(dir_to_make)
        print_to_console(client_id, 'Created directory {0} successfully.'.format(dir_to_make))
        return True
    return False


# Creates a new, empty text file locally. Doesn't create remote copy as the file is empty.
def create_new_empty_file(file_path, file_name, client_id):
    full_file_path = file_path + "/" + file_name
    absolute_dir_path = os.path.abspath(file_path)

    # First check if the requested directory exists
    if os.path.exists(absolute_dir_path):
        # Directory exists
       if os.path.exists(full_file_path) and os.path.getsize(full_file_path) >= 0:
           # File exists and isn't empty - do not overwrite.
           print_to_console(client_id, "File {0} already exists - will not overwrite contents.".format(file_name))
       else:
           # File doesn't exist: create a new empty text file here.
           new_file = open(full_file_path, "w+")
           new_file.close()
           print_to_console(client_id, "Created new file {0} successfully.".format(file_name))
       return True
    else:
        # Directory doesn't exist
        while(True):
            create_new_dir = raw_input("Directory {0} doesn't exist: do you want to create it now? (enter y/n): ".format(file_path))
            if str(create_new_dir).__contains__("y"):
                mkdir(file_path, client_id)
                new_file = open(full_file_path, 'w+')
                new_file.close()
                print_to_console(client_id, 'Created new file {0} successfully.'.format(file_name))
                return True
            elif str(create_new_dir).__contains__("n"):
                print_to_console(client_id, "Couldn't create file {0}.".format(full_file_path))
                return False
            else:
                print_to_console(client_id, 'Invalid answer {0} - try again!')


# Reads the specified file from the remote copy. Requires getting the remote mapping from the directory server, and then requesting the file from the fileserver directly.
# Utilises client-side caching, and waits for write locks to be released if necessary.
def read_file(file_path, file_name, client_id, cache):
    try:
        full_file_path = file_path + "/" + file_name
        print_to_console(client_id, "Client requested to read " + full_file_path)
        server_address, server_id, file_id, file_version = get_file_mapping_from_directory_server(full_file_path, client_id)

        if file_id is None:
            print_to_console(client_id, "{0} doesn't exist as a remote copy.".format(full_file_path))
            return

        if cache.is_entry_cached_and_up_to_date(full_file_path, file_version):
            # Don't bother going to file server to fetch contents
            cache_entry = cache.fetch_cache_entry(full_file_path)
            print_to_console(client_id, 'Opening local copy to update with response contents: {0}'.format(cache_entry['file_contents']))
            with open(full_file_path, 'r+') as edit_file:
                edit_file.write(cache_entry['file_contents'])

        else:
            # request the file from this file server
            while not acquire_lock_on_file(file_id, client_id):
                pass
            response = requests.get(
                file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_server_id': server_id})
            file_contents = response.json()['file_contents']
            if file_contents is not None:
                print_to_console(client_id, 'Updating file with response contents...')
                with open(full_file_path, 'r+') as edit_file:
                    edit_file.write(file_contents)

            # Add this to the cache
            cache.add_cache_entry(full_file_path, file_contents, file_version)
        open_file_in_text_editor(full_file_path, client_id)

    except Exception as e:
        print_to_console(client_id, "Exception caught in read_file method: {0}".format(str(e)))


# Writes to the local and remote copies of the specified file. IF the file doesn't exist, it will be created.
# Obtains mapping from directory server if file already exists, and pushes the changes to the remote copy. If this file didn't exist as a remote copy, the changes are pushed directly by the directory server.
# Uses write-locking in order to ensure atomicity of concurrent updates to the same file.
def write_file(file_path, file_name, client_id, cache):
    try:
        full_file_path = file_path + "/" + file_name
        print_to_console(client_id, "Writing to " + full_file_path)

        # open file for writing
        if not os.path.exists(full_file_path):
            print_to_console(client_id, 'File {0} does not exist for writing: will create a new empty file locally.'.format(full_file_path))
            create_new_empty_file(file_path, file_name, client_id)
        if not os.path.exists(full_file_path):
            print_to_console(client_id, "Cannot write to file {0} as it does not exist.".format(full_file_path))
            return

        # display the file in the text editor for writing
        open_file_in_text_editor(full_file_path, client_id)
        file_contents = open(full_file_path, 'r').read()

        # locate the remote copy by consulting the directory server
        server_address, server_id, file_id, file_version, new_remote_copy_created = post_request_to_directory_server_for_file_mapping(full_file_path, file_contents, client_id)
        if server_id is None:
            print_to_console(client_id,
                             "There are no file servers registered with the directory server: cannot store remotely.\n Please register at least one fileserver!")
            return

        if not new_remote_copy_created:
            # we are updating an existing file on this file server
            print_to_console(client_id, 'Updating existing remote copy of {0} with new changes...'.format(full_file_path))
            while not acquire_lock_on_file(file_id, client_id):
                pass

            # We know where the remote copy is and have the lock: post our updates to the remote copy
            requests.post(file_api.create_url(server_address[0], server_address[1], ""), json={'file_id': file_id, 'file_contents': file_contents})

            # Now make sure the directory server knows we have a new revision of the remote copy
            file_version += 1
            directory_server_response = requests.post(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], "update_file_version"), json={'file_id':file_id, 'file_version':file_version, 'file_server_id': server_id, 'file_name': full_file_path})
            if directory_server_response.json()['version_updated']:
                print_to_console(client_id, 'Updated version on directory server successfully.')
            else:
                print_to_console(client_id,
                                 "Couldn't update the version of the remote copy as expected. Consult directory server logging output for details.")
            release_lock_on_file(file_id, client_id)
        else:
            # The remote copy didn't exist until our post request: we have created a new remote copy for this file
            print_to_console(client_id, 'Created new remote copy of {0} on file server {1}.'.format(file_path, server_id))

        cache.add_cache_entry(full_file_path, file_contents, file_version)
    except Exception as e:
        print_to_console(client_id, "Exception caught in write_file method: {0}".format(e.message))


# Opens the local copy of a file in the system web browser, if it exists.
def open_file(file_path, file_name, client_id):
    full_file_path = file_path + "/" + file_name
    absolute_dir_path = os.path.abspath(full_file_path)
    print_to_console(client_id, "Opening " + full_file_path + " in console as read-only.")
    if os.path.exists(full_file_path):
        print '----- '+ full_file_path + ' CONTENTS' + ' -----'
        f = open(full_file_path, 'r')
        print f.read()
    else:
        print_to_console(client_id, "{0} doesn't exist".format(full_file_path))


# ---------------------------#
# ---- DIRECTORY SERVER ---- #
# ---------------------------#


# Fetches the mapping details of the requested file and details of the file-server on which it is stored. Used for read requests.
def get_file_mapping_from_directory_server(full_file_path, client_id):
    print_to_console(client_id, "Getting {0} mapping from directory server.".format(full_file_path))
    response = requests.get(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={'file_name': full_file_path})

    # Extract the info we want
    file_server_address = response.json()['file_server_address']
    file_id = response.json()['file_id']
    file_server_id = response.json()['file_server_id']
    file_version = response.json()['file_version']

    return file_server_address, file_server_id, file_id, file_version


# Fetches the mapping details for an existing remote copy, or else creates a new mapping and provides the details if the remote copy didn't exist previously. Used for write requests.
def post_request_to_directory_server_for_file_mapping(full_file_path, file_contents, client_id):
    print_to_console(client_id, "Posting {0} to directory server and extracting mapping from response.".format(full_file_path))
    response = requests.post(file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={'file_name': full_file_path, 'file_contents': file_contents})

    # Extract the info we want
    file_server_address = response.json()['file_server_address']
    file_server_id = response.json()['file_server_id']
    file_id = response.json()['file_id']
    file_version = response.json()['file_version']
    new_remote_copy_created = response.json()['new_remote_copy']

    return file_server_address, file_server_id, file_id, file_version, new_remote_copy_created


# ---------------------------#
# ----- LOCKING SERVER ----- #
# ---------------------------#


# Sends a registration request to the locking server.
# Ensures that a client cannot start up until it has registered with a locking server.
# Also ensures that only a registered client can place a lock on a file.
def register_with_locking_server(client_id):
    print_to_console(client_id, 'Sending request to register client {0} with locking server..'.format(client_id))
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
        print_to_console(client_id, 'Registered with locking server.')
    else:
        print_to_console(client_id, 'Client could not register with locking server')


# Sends a request to the locking server to lock the specified file.
# Allows a client to place a write-lock on a file by contacting the locking server. This lock will time out if not cleared after a certain period.
def acquire_lock_on_file(file_id, client_id):
    response = requests.put(file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], ""),
                            json={'file_id': file_id, 'client_id': client_id})
    locked = response.json()['locked']
    if not locked or locked is None:
        return False
    else:
        print_to_console(client_id, "Client{0} has locked file {1}".format(client_id, file_id))
        return True


# Allows a client to clear a write-lock on a file by contacting the locking server.
def release_lock_on_file(file_id, client_id):
    response = requests.delete(file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], ""),
                               json={'file_id': file_id, 'client_id': client_id})
    locked = response.json()['locked']
    if locked is None:
        print_to_console(client_id, 'The client is not registered with the locking server - cannot unlock the file!')
        return None
    elif locked is False:
        print_to_console(client_id, "File {0} has been unlocked".format(file_id))
        return True
    else:
        print_to_console(client_id, 'The lock could not be removed')
        return False


# Allows a client to determine whether a file is already locked by contacting the locking server.
def is_file_locked(file_id, client_id):
    response = requests.get(file_api.create_url(LOCKING_SERVER_ADDRESS[0], LOCKING_SERVER_ADDRESS[1], ""),
                            json={'file_id': file_id})

    locked = response.json()['locked']
    if locked is False or locked is None:
        print_to_console(client_id, "File {0} isn't locked".format(file_id))
        return False
    else:
        print_to_console(client_id, "File {0} is locked".format(file_id))
        return True
