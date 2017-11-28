#
# A RESTful server implementation. Modelling an NFS fileserver.
# Uses HTTP requests.
# The fileserver should know where to find the directory server.
#

import sys
from flask_restful import Resource, Api
from flask import Flask

app = Flask(__name__)
api = Api(app)

# Directory server started at default Flask address for ease
DIRECTORY_SERVER_ADDRESS = "http://127.0.0.1:5000"


class FileServer(Resource):

    def get(self, requested_file_id):
        #will read the data out to the requesting node
        if
        return {"data": "insert file contents here"}

    def post(self, requested_file_id):
        # will write the incoming request data to the fileserver version of the file
        return "", # no content to return


# this adds a url handle for the FileServer
# TODO generate some sort of an ID, since we may have multiple file servers eventually
api.add_resource(FileServer, '/')

if __name__ == "__main__":
    app.run(debug=True, port=int(sys.argv[1]))
