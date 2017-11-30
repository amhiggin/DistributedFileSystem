from flask_restful import Resource, Api
from flask import Flask, request
import sys

app = Flask(__name__)
api = Api(app)

# maintain list of locked files
LOCKED_FILES_BY_ID = {}


class LockingServer(Resource):

    # we want to put a value in the lookup table
    def put(self):
        print 'In lock server put method - trying to acquire the lock for the file'

        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']
        if file_id in LOCKED_FILES_BY_ID
            if not LOCKED_FILES_BY_ID[file_id]:
                # take the lock
                LOCKED_FILES_BY_ID[file_id] = True
                print 'Client {0} has successfully locked file {1}'.format(client_id, file_id)
                return{'lock': True}
            return {'lock': False}
        else:
            LOCKED_FILES_BY_ID[file_id] = True
            return {'lock': True}

    # we want to delete a value from the lookup table
    def delete(self, requested_file_id):
        print 'In lock server delete method - trying to release the lock for the file'
        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']

        if file_id in LOCKED_FILES_BY_ID:
            if LOCKED_FILES_BY_ID[file_id] == True:
                # release the lock
                LOCKED_FILES_BY_ID[file_id] = False
        return {'lock': False}


    def get(self):
        print 'In lock server get method: checking whether file is locked or not'
        file_id = request.get_json()['file_id']
        if file_id in LOCKED_FILES_BY_ID:
            if LOCKED_FILES_BY_ID[file_id][1] == True:
                return {'locked': True}
            else:
                return {'locked':False}
        return {'locked': False}


# this adds a url handle for the Locking Server
api.add_resource(LockingServer, '/')

if __name__ == "__main__":
    # specify the host to run it on
    app.run(debug=True, port=int(sys.argv[1]))
