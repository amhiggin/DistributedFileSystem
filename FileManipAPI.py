#
# These are methods that can be used between the fileserver and the client.
#
import os
import requests
import flask_restful
from flask import Flask, request

# Directory server started at default Flask address for ease
DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)

def create_root_dir_if_not_exists(root_path):
    if not os.path.exists(root_path):
        os.mkdir(root_path)


# create a url to query
def create_url(ip, port, endpoint):
    url = "http://{0}:{1}/{2}".format(ip, port, endpoint)
    print "Creating url: {0}".format(url)
    return url


# This method fetches the details of the file and server on which it is stored
def get_file_mapping_from_directory_server(file_path, file_name):
    # TODO test whether we need the file_path too
    print  "Sending request to directory server for file {0}".format(file_name)
    response = requests.get(create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={"file_name": file_name})

    print 'Response from server: {0}'.format(response.json())
    file_server_address = response.json['file_server_address']
    print 'File server address is {0}:{1}'.format(file_server_address[0], file_server_address[1])
    file_id = response.json['file_id']
    print 'File id is {0}:{1}'.format(file_id)
    file_server_id = response.json['file_server_id']
    print 'File server id is {0}:{1}'.format(file_server_id)

    return file_server_address, file_server_id, file_id


def post_request_to_directory_server_for_file_mapping(file_path, file_name, contents_to_write):
    print "Sending request to post update to file {0} from directory server"
    response = requests.post(create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), json={"file_name": file_name, "contents_to_write": contents_to_write})

    print 'Response from server: {0}'.format(str(response.json()))
    file_server_address = response.json['file_server_address']
    file_server_id = response.json['file_server_id']
    file_id = response.json['file_id']
    new_remote_copy_created = response.json['new_remote_copy']

    return file_server_address, file_server_id, file_id, new_remote_copy_created


# gets a name for the file, equal to the file id
def get_serverside_file_name_by_id(file_id):
    return str(file_id) + '.txt'

