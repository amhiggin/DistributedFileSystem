#
# A RESTful server implementation. Modelling an NFS file-server.
# Managed and load-balanced by the directory server, which is available at a defined address.
#

import requests
import shutil
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import FileManipAPI as file_api

app = Flask(__name__)
api = Api(app)

DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)
LOCKING_SERVER_ADDRESS = ("127.0.0.1", 5001)
SERVER_ID = "" # Given to us by the directory server.
ROOT_DIR = "Server" # Updated at startup with the ID assigned by the directory server.


'''                  '''
''' COMMON FUNCTIONS '''
'''                  '''

# Prints the given message to the console, including the name of the file-server.
def print_to_console(message):
    print ("FileServer%s: %s" % (SERVER_ID, message))


# Deletes any old root directory under the given name.
def clean_up_old_root_dir_if_exists(root_dir):
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
        print_to_console("Removed old {0} directory".format(root_dir))


'''                      '''
''' RESOURCE DEFINITIONS '''
'''                      '''

class FileServer(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('server_id')

    def get(self):
        # extract the requested file's identifier
        file_id = request.get_json()['file_id']
        # construct the filename from the file id, if the file exists
        file_name = ROOT_DIR + "/" + file_api.get_serverside_file_name_by_id(file_id)
        with open(file_name, 'r') as in_file:
            file_contents = in_file.read()
        print_to_console("File {0} exists: sending a copy to the client as requested.".format(file_name))
        return {'file_contents': file_contents}

    def post(self):
        # get required file data
        file_contents = request.get_json()['file_contents'].strip()
        file_id = request.get_json()['file_id']
        file_name = ROOT_DIR + "/" + file_api.get_serverside_file_name_by_id(file_id)

        with open(file_name, 'r+') as edit_file:
            edit_file.write(str(file_contents))
            print_to_console('Wrote update to file {0} as requested.'.format(file_id))
        return {'file_contents': file_contents}


# create a new remote copy if a remote copy doesn't exist.
# This request will be sent by the directory server when creating a new mapping.
class CreateNewRemoteCopy(Resource):

    def post(self):
        # extract the details of the file
        file_id = request.get_json()['file_id']
        file_contents = request.get_json()['file_contents']

        # construct a new filename from the file id.
        file_name = ROOT_DIR + "/" + file_api.get_serverside_file_name_by_id(file_id)
        print_to_console("Request received to create new file {0}".format(file_name))

        # write the contents to a new remote "master" copy
        file_to_write = open(file_name, 'w+')
        file_to_write.write(file_contents)
        file_to_write.close()

        # Send an update back to the directory server
        if os.path.exists(file_name):
            print_to_console("Remote copy of file id {0} successfully created.".format(file_id))
            return {'new_remote_copy': True}
        else:
            print_to_console("Remote copy of file id {0} could not be created.".format(file_id))
            return {'new_remote_copy': False}


api.add_resource(FileServer, '/')
api.add_resource(CreateNewRemoteCopy, '/create_new_remote_copy')


if __name__ == "__main__":
    if len(sys.argv) == 3:
        if os.environ.get("WERKZEUG_RUN_MAIN") == 'true':
            print_to_console("Hello, I'm a Fileserver! Lets register with the directory server...")
            # Send a request to the directory server to get our ID
            url =  file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1],"register_fileserver")
            print_to_console("Connecting ...")
            while True:
                try:
                    response = requests.post(url, json={'ip': sys.argv[1], 'port': sys.argv[2]})
                    print_to_console("Connected.")
                    break
                except:
                    # Probably stil waiting for the directory service to start up
                    pass
            SERVER_ID = response.json()['server_id']
            print_to_console("Successfully registered as server {0}".format(SERVER_ID))

            # Now create our own root directory, deleting any old existing one of the same name.
            ROOT_DIR = ROOT_DIR + str(SERVER_ID)
            clean_up_old_root_dir_if_exists(ROOT_DIR)
            file_api.create_root_dir_if_not_exists(ROOT_DIR)
            print_to_console("Created new {0} root directory".format(ROOT_DIR))

        app.run(debug=True, host=sys.argv[1], port=int(sys.argv[2]))
    else:
        print_to_console("IP address and port weren't entered correctly for the fileserver: cannot launch.")
    exit(0)
