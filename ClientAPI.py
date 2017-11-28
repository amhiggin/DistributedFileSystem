#
# This is the library of function calls that the client will be able to use.
# It should allow for read, write, etc. (possibly locking also).
# Should handle talking to each of the servers to route the response back to the client.
#

import os, sys
import flask
import flask_restful
import requests
import FileManipAPI as FILE_API
from sys import platform as _platform

# Directory server started at default Flask address for ease
DIRECTORY_SERVER_ADDRESS = "http://127.0.0.1:5000"

# opens file in windows or linux default system text editor
def open_file_in_text_editor(full_file_path):
    if _platform == "linux" or _platform == "linux2":
        os.system('%s %s' % (os.getenv('EDITOR'), full_file_path))
    elif _platform == "win32" or "win64":
        os.system("start " + full_file_path)


# create a url to query
def create_url(ip, port, args):
    return "http://" + ip + ":" + port + "/" + args

# download a copy of the file from the file-server
# should inform lock server of the fact that it has a copy
# TODO will need to add this file to the list of locked files
def read_file(file_path, file_name):
    print "Request to read " + file_path + "/" + file_name

    # get whatever is available on hardcoded single fileserver URL
    response = requests.get(create_url("127.0.0.1", "45678", {file_path, file_name}))
    return response.json()['data'].strip()


# upload a changed copy of the file
# should inform the lock server of the fact that it is updating a copy
def write_file(file_path, file_name, contents_to_write):
    print "Request to write " + file_path + "/" + file_name
    requests.post(create_url("127.0.0.1", "45678", ""), json={'data': contents_to_write})
    # no response needed from post


# check the file exists on the fileserver, as such
def open_file(file_path, file_name):
    print "Request to open " + file_path + "/" + file_name
    # NOT implemented yet


# doesn't really do anything effective (from what I can see)
def close_file(file_path, file_name):
    print "Request to close " + file_path + "/" + file_name
    # NOT implemented yet

# -----------------#

# Placeholder directory server methods
def get_file_mapping_from_directory_server(file_path, file_name):
    # make a get call to the directory server at the URL
    # response should be an id corresponding to this file
    print "Client wants to get file mapping for " + file_path + "/" + file_name + " from directory server"
    response = requests.get(DIRECTORY_SERVER_ADDRESS, {file_path, file_name})
    file_id = response.json()['file_id'].strip()
    print "File id returned was: " + file_id
    return file_id
#------------------#

#plcaeholder lock server methods
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


