from flask_restful import Resource, Api
from flask import Flask, request
import sys

app = Flask(__name__)
api = Api(app)

# maintain list of locked files
LOCKED_FILES_BY_ID = {}


def print_to_console(self, message):
    print ("LockingServer: %s" % message)



class LockingServer(Resource):

    def put(self):
        print_to_console('In lock server put method - trying to acquire the lock for the file')

        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']
        if file_id in LOCKED_FILES_BY_ID:
            if not LOCKED_FILES_BY_ID[file_id]:
                # take the lock
                LOCKED_FILES_BY_ID[file_id] = True
                print_to_console('Client {0} has successfully locked file {1}'.format(client_id, file_id))
                return{'lock': True}
            print_to_console("Client {0} couldn't lock file {1}".format(client_id, file_id))
            return {'lock': False}
        else:
            LOCKED_FILES_BY_ID[file_id] = True
            print_to_console('Client {0} has successfully locked file {1}'.format(client_id, file_id))
            return {'lock': True}

    # we want to delete a value from the lookup table
    def delete(self):
        print_to_console('In lock server delete method - trying to release the lock for the file')
        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']

        if file_id in LOCKED_FILES_BY_ID:
            if LOCKED_FILES_BY_ID[file_id] == True:
                # release the lock
                LOCKED_FILES_BY_ID[file_id] = False
                print_to_console('Client {0} has unlocked file {1}'.format(client_id, file_id))
        # in either case, we return that the file is unlocked
        else:
            print_to_console('File {0} was never locked!'.format(file_id))
        return {'lock': False}


    def get(self):
        print_to_console('In lock server get method: checking whether file is locked or not')
        file_id = request.get_json()['file_id']
        if file_id in LOCKED_FILES_BY_ID:
            if LOCKED_FILES_BY_ID[file_id][1] == True:
                print_to_console('File {0} is locked'.format(file_id))
                return {'locked': True}
            else:
                print_to_console('File {0} is not locked'.format(file_id))
                return {'locked':False}
        print_to_console('File {0} is not locked'.format(file_id))
        return {'locked': False}


# this adds a url handle for the Locking Server
api.add_resource(LockingServer, '/')

if __name__ == "__main__":
    app.run(debug=True, host=sys.argv[1], port=int(sys.argv[2]))
