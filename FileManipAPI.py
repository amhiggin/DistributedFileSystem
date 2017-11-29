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
    print "Creating url"
    return "http://{0}:{1}/{2}".format(ip, port, endpoint)


# This method fetches the details of the file and server on which it is stored
def get_file_mapping_from_directory_server(file_path, file_name):
    request = {'file_name': file_name}
    response = requests.get(create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1], ""), params=request)

    # Response from directory server should provide all of these params
    file_server_address = response.json['file_server_address']
    file_server_id = response.json['file_server_id']
    file_id = response.json['file_id']

    return file_server_address, file_server_id, file_id


# gets a name for the file, equal to the file id
def get_serverside_file_name_by_id(file_id):
    return str(file_id) + '.txt'

