#
# A RESTful server implementation. Modelling an NFS fileserver.
# Will use get and post requests with HTTP response codes.
# The fileserver should know where to find the directory server.
#

import sys
from flask_restful import Resource, Api
from flask import Flask

app = Flask(__name__)
api = Api(app)

DIRECTORY_SERVER_ADDRESS = "x:y" #TODO implement later


class FileServer(Resource):
    def get(self, requested_file:
        return {"Hello": "World"}

    def post(self, requested_file):
        # TODO implement what this does
        return "", # no content to return


# this adds a url handle for the FileServer
# TODO generate some sort of an ID, since we may have multiple fileservers eventually
api.add_resource(FileServer, '/')

if __name__ == "__main__":
    app.run(debug=True, port=int(sys.argv[1]))
