#
# A RESTful server implementation. Modelling an NFS fileserver.
# Will use get and post requests with HTTP response codes.
#

import sys
from flask_restful import Resource, Api
from flask import Flask

app = Flask(__name__)
api = Api(app)


class FileServer(Resource):
    def get(self):
        return {"Hello": "World"}, 200

    def post(self):
        # TODO implement what this does
        # no content to return
        return "", 204


# this adds a url handle for the FileServer
# TODO generate some sort of an ID, since we may have multiple fileservers eventually
api.add_resource(FileServer, '/')

if __name__ == "__main__":
    app.run(debug=True, port=int(sys.argv[1]))
