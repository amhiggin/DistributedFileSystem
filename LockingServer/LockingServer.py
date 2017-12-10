from flask_restful import Resource, Api
from flask import Flask, request
import sys
import datetime

app = Flask(__name__)
api = Api(app)

# maintain list of locked files
LOCKED_FILES_BY_ID = {}
TIMEOUT = 5000


def print_to_console(message):
    print ("LockingServer: %s" % message)


def timeout_on_lock(locked_files_by_id, file_id):
    locked_time = LOCKED_FILES_BY_ID[file_id]['timestamp']
    current_time = str(datetime.datetime.now())

    if (int(current_time) - int(locked_time)) >= TIMEOUT:
        return True
    else:
        return False



class LockingServer(Resource):

    def put(self):
        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']
        current_time = str(datetime.datetime.now())

        if file_id in LOCKED_FILES_BY_ID:
            if timeout_on_lock():
                LOCKED_FILES_BY_ID[file_id] = {'locked': False, 'timestamp': ''}
            if not LOCKED_FILES_BY_ID[file_id]:
                # take the lock
                LOCKED_FILES_BY_ID[file_id] = {'locked': True, 'timestamp': current_time}
                print_to_console('Client {0} has successfully locked file {1}'.format(client_id, file_id))
                return{'lock': True}
            else:
                print_to_console("Client {0} couldn't lock file {1}".format(client_id, file_id))
                return {'lock': False}
        else:
            LOCKED_FILES_BY_ID[file_id] = {'locked': True, 'timestamp': current_time}
            print_to_console('Client {0} has successfully locked file {1}'.format(client_id, file_id))
            return {'lock': True}

    # we want to delete a value from the lookup table
    def delete(self):
        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']

        if file_id in LOCKED_FILES_BY_ID:
            if LOCKED_FILES_BY_ID[file_id]['locked'] == True:
                # release the lock
                LOCKED_FILES_BY_ID[file_id]['locked'] = False
                print_to_console('Client {0} has unlocked file {1}'.format(client_id, file_id))
        # in either case, we return that the file is unlocked
        else:
            print_to_console('File {0} was never locked!'.format(file_id))
        return {'lock': False}


    def get(self):
        print_to_console('In lock server get method: checking whether file is locked or not')
        file_id = request.get_json()['file_id']
        if file_id in LOCKED_FILES_BY_ID:
            if LOCKED_FILES_BY_ID[file_id]['locked'] == True:
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
