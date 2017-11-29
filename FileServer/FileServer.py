#
# A RESTful server implementation. Modelling an NFS fileserver.
# Managed and load-balanced by the directory server, which is available at a defined address.
#

import sys
from flask_restful import Resource, Api, reqparse
from flask import Flask, request
import FileManipAPI as file_api

app = Flask(__name__)
api = Api(app)

# Directory server started at default Flask address for ease
DIRECTORY_SERVER_ADDRESS = "http://127.0.0.1:5000"


def print_to_console(self, message):
    print ("FileServer%s: %s%s" % (self.parser.parse_args()['file_id'], message, '\n'))


class FileServer(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        # the server id should be assigned by the directory server
        self.parser.add_argument('server_id')


    def get(self, requested_file_id):
        # will read the data out to the requesting node
        file_name = file_api.get_serverside_file_name_by_id(requested_file_id)
        with open(file_name, 'r') as in_file:
            file_text = in_file.read()
        return {'data': file_text}

    def post(self, requested_file_id):
        # will write the incoming request data to the fileserver version of the file
        file_edits = request.form['data']
        print_to_console(self, file_edits)
        with open(requested_file_id, 'r+') as edit_file:
            edit_file.write(file_edits)
            final_version = edit_file.read()
        return {'data': final_version}


# this adds a url handle for the FileServer
# TODO generate some sort of an ID, since we may have multiple file servers eventually
api.add_resource(FileServer, '/')

if __name__ == "__main__":
    app.run(debug=True, port=int(sys.argv[1]))
