from flask_restful import Resource, Api
from flask import Flask
import sys

app = Flask(__name__)
api = Api(app)

# maintain list of locked files
LOCKED_FILES = {}


class LockingServer(Resource):

    # we want to put a value in the lookup table
    def put(self, requested_file):
        print ' In lock server put method'
        # add an index for this file
        # LOCKED_FILES[i] = True

    # we want to delete a value from the lookup table
    def delete(self, requested_file):
        # TODO implement what this does
        return "", # no content to return


# this adds a url handle for the Locking Server
api.add_resource(LockingServer, '/')

if __name__ == "__main__":
    # specify the host to run it on
    app.run(debug=True, port=int(sys.argv[1]))
