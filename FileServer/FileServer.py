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
        # FIXME this id should also be part of the root dir
        self.parser.add_argument('server_id')


    def get(self):
        # construct the filename from the server id and file id
        server_id = self.parser.parse_args()['server_id']
        file_name = server_id + "/" + file_api.get_serverside_file_name_by_id(request.json()['file_id'])

        with open(file_name, 'r') as in_file:
            file_text = in_file.read()
        return {'data': file_text}

    def post(self):
        # will write the incoming request data to the fileserver version of the file
        server_id = self.parser.parse_args()['server_id']
        file_edits = request.form['data']
        print_to_console(self, file_edits)
        file_name = server_id + '/' + file_api.get_serverside_file_name_by_id(request.json()['file_id'])

        with open(file_name, 'r+') as edit_file:
            edit_file.write(file_edits)
            final_version = edit_file.read()
        return {'data': final_version}


# this adds a url handle for the FileServer
api.add_resource(FileServer, '/')


if __name__ == "__main__":
    print_to_console("Hello, I'm a Fileserver! Lets register with the directory server...")
    if len(sys.argv) == 3:
        if os.environ.get("WERKZEUG_RUN_MAIN") == 'true':
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
