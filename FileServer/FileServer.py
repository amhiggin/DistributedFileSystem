#
# A RESTful server implementation. Modelling an NFS fileserver.
# Managed and load-balanced by the directory server, which is available at a defined address.
#

import sys, requests, json, os
from flask_restful import Resource, Api, reqparse
from flask import Flask, request

import FileManipAPI as file_api

app = Flask(__name__)
api = Api(app)

DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)
LOCKING_SERVER_ADDRESS = "" # TODO @Amber
SERVER_ID = "" # used for console messages
ROOT_DIR = "Server" # updated at startup with the specific number


def print_to_console(message):
    print ("FileServer%s: %s%s" % (SERVER_ID, message, '\n'))


class FileServer(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('server_id')


    def get(self):
        # construct the filename from the server id and file id
        file_id = request.json()['file_id']
        file_name = ROOT_DIR + "/" + file_api.get_serverside_file_name_by_id(file_id)

        with open(file_name, 'r') as in_file:
            file_contents = in_file.read()
        return {'file_contents': file_contents}

    def post(self):
        # will write the incoming request data to the fileserver version of the file
        file_contents = request.json()['file_contents']
        print_to_console(file_contents)
        file_id = request.json()['file_id']
        file_name = ROOT_DIR + "/" + file_api.get_serverside_file_name_by_id(file_id)

        with open(file_name, 'r+') as edit_file:
            edit_file.write(file_contents)
            file_contents = edit_file.read()
        return {'file_contents': file_contents}


# create a new remote copy if a remote copy doesn't exist
class CreateNewRemoteCopy(Resource):

    def post(self):
        file_id = request.get_json()['file_id']
        print_to_console("Request received to create new file for file {0}".format(file_id))
        file_contents = request.get_json()['file_contents']
        print_to_console("File contents: ".format(file_contents))

        # have to get the text-file equivalent name for this file id
        file_name = ROOT_DIR + "/" + file_api.get_serverside_file_name_by_id(file_id)
        print_to_console("File name: {0}".format(file_name))

        # write the contents to a new remote "master" copy
        file_to_write = open(file_name, 'w+')
        file_to_write.write(file_contents)
        file_to_write.close()
        if os.path.exists(file_name):
            print "Remote copy of file id {0} successfully created".format(file_id)
            return {'new_remote_copy': True}
        else:
            print "Remote copy of file id {0} could not be created".format(file_id)
            return {'new_remote_copy': False}

# this adds a url handle for the FileServer
api.add_resource(FileServer, '/')
api.add_resource(CreateNewRemoteCopy, '/create_new_remote_copy')


if __name__ == "__main__":
    if len(sys.argv) == 3:
        if os.environ.get("WERKZEUG_RUN_MAIN") == 'true':
            print_to_console("Hello, I'm a Fileserver! Lets register with the directory server...")
            print_to_console("Correct args passed: {0}:{1}".format(sys.argv[1], sys.argv[2]))
            print_to_console("sending request to directory server")
            url =  file_api.create_url(DIRECTORY_SERVER_ADDRESS[0], DIRECTORY_SERVER_ADDRESS[1],"register_fileserver")
            print_to_console("Connecting to {0}".format(str(url)))
            response = requests.post(url, json={'ip': sys.argv[1], "port": sys.argv[2]})
            SERVER_ID = response.json()['server_id']
            ROOT_DIR = ROOT_DIR + str(SERVER_ID)
            print_to_console("Successfully registered as server {0}".format(SERVER_ID))
            file_api.create_root_dir_if_not_exists(ROOT_DIR)
            print_to_console("Server root dir set to {0}".format(ROOT_DIR))
        app.run(debug=True, host=sys.argv[1], port=int(sys.argv[2]))
else:
    print_to_console("IP address and port weren't entered for the fileserver: cannot launch")
