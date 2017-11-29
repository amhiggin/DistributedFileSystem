#
# A RESTful server implementation. Modelling an NFS fileserver.
# Uses HTTP requests.
# The fileserver should know where to find the directory server.
#

import sys
from flask_restful import Resource, Api
from flask import Flask, request

app = Flask(__name__)
api = Api(app)

# Directory server started at default Flask address for ease
DIRECTORY_SERVER_ADDRESS = "http://127.0.0.1:5000"
SERVER_ID = ""


def print_to_console(message):
    print ("FileServer%s: %s%s" % (SERVER_ID, message, '\n'))


class FileServer(Resource):

    def get(self, requested_file_id):
        # will read the data out to the requesting node
        with open(requested_file_id, 'r') as in_file:
            file_text = in_file.read()
        return {'data': file_text}

    def post(self, requested_file_id):
        # will write the incoming request data to the fileserver version of the file
        file_edits = request.form['data']
        print 'Edits to file: ' + file_edits
        with open(requested_file_id, 'r+') as edit_file:
            edit_file.write(file_edits)
            final_version = edit_file.read()
        return {'data': final_version}


# this adds a url handle for the FileServer
# TODO generate some sort of an ID, since we may have multiple file servers eventually
api.add_resource(FileServer, '/')

if __name__ == "__main__":
    app.run(debug=True, port=int(sys.argv[1]))
