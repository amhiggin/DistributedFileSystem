from flask_restful import Resource, Api
from flask import Flask
import sys

app = Flask(__name__)
api = Api(app)

# maintain list of locked files
LOCKED_FILES = {}


class LockingServer(Resource):

    # we want to put a value in the lookup table
    def put(self, requested_file_id):
        print 'In lock server put method - trying to acquire the lock for the file'
        # add some conditional logic
        LOCKED_FILES[requested_file_id] = True

    # we want to delete a value from the lookup table
    def delete(self, requested_file_id):
        # TODO implement what this does
        print 'In lock server delete method - trying to release the lock for the file'
        LOCKED_FILES[requested_file_id] = False
        return "", # no content to return

    def get(self, requested_file_id):
        # Return whether or not a paricular file is locked
        print 'In lock server get method: checking whether file is locked or not'


# this adds a url handle for the Locking Server
api.add_resource(LockingServer, '/')

if __name__ == "__main__":
    # specify the host to run it on
    app.run(debug=True, port=int(sys.argv[1]))
