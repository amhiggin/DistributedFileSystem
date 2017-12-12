from flask_restful import Resource, Api
from flask import Flask, request
import sys
import datetime

app = Flask(__name__)
api = Api(app)

# maintain list of locked files
LOCKED_FILES_BY_ID = {}
REGISTERED_CLIENTS_BY_ID = {}
TIMEOUT = 60


def print_to_console(message):
    print ("LockingServer: %s" % message)

# This method is a safety mechanism, such that if a client dies a file will not be infinitely locked.
def timeout_on_lock(locked_files_by_id, file_id):
    locked_time = LOCKED_FILES_BY_ID[file_id]['timestamp']
    current_time = datetime.datetime.now()
    difference = current_time - locked_time
    if difference >= datetime.timedelta(seconds=TIMEOUT):
        return True
    else:
        return False

class LockingServer(Resource):

    def put(self):
        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']
        if not client_id in REGISTERED_CLIENTS_BY_ID.keys():
            print_to_console("Client {0} is not registered with the locking server! Can't place a lock.".format(client_id))
            return {'locked': None}
        current_time = datetime.datetime.now()


        if file_id in LOCKED_FILES_BY_ID:
            if LOCKED_FILES_BY_ID[file_id]['locked'] == True:
                if timeout_on_lock(LOCKED_FILES_BY_ID, file_id):
                    print_to_console("Timeout reached on file {0}: unlocking".format(file_id))
                    LOCKED_FILES_BY_ID[file_id] = {'locked': False, 'timestamp': None, 'client_id': None}
            if LOCKED_FILES_BY_ID[file_id]['locked'] is False or LOCKED_FILES_BY_ID[file_id]['locked'] is None:
                # take the lock
                LOCKED_FILES_BY_ID[file_id] = {'locked': True, 'timestamp': current_time, 'client_id':client_id}
                print_to_console('Client {0} has successfully locked file {1}'.format(client_id, file_id))
                return{'locked': True}
            else:
                print_to_console("Client {0} couldn't lock file {1}".format(client_id, file_id))
                return {'locked': False}
        else:
            LOCKED_FILES_BY_ID[file_id] = {'locked': True, 'timestamp': current_time, 'client_id':client_id}
            print_to_console('Client {0} has successfully locked file {1}'.format(client_id, file_id))
            return {'locked': True}

    # we want to delete a value from the lookup table
    def delete(self):
        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']
        if not client_id in REGISTERED_CLIENTS_BY_ID.keys():
            print_to_console("Client {0} is not registered with the locking server! Can't release a lock.".format(client_id))
            return {'locked': None}

        if file_id in LOCKED_FILES_BY_ID.keys():
            if LOCKED_FILES_BY_ID[file_id]['locked'] == True and LOCKED_FILES_BY_ID[file_id]['client_id'] is client_id:
                # we have the lock - we can unlock it now
                LOCKED_FILES_BY_ID[file_id]['locked'] = False
                print_to_console('Client {0} has unlocked file {1}'.format(client_id, file_id))
                return {'locked': False}
            else:
                return {'locked':True}
        # in either case, we return that the file is unlocked
        else:
            if LOCKED_FILES_BY_ID[file_id]['client_id'] is not client_id:
                print "We weren't the ones who locked the file: can't unlock it!"
                return {'locked': None}
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

class RegisterClientInstance(Resource):

    def get(self):
        client_id = request.get_json()['client_id']
        response = {'registered': True}
        REGISTERED_CLIENTS_BY_ID[client_id] = response
        print_to_console("RECEIVED REQUEST FROM CLIENT {0}. REGISTERED SUCCESSFULLY.".format(client_id))
        return response


# this adds a url handle for the Locking Server
api.add_resource(LockingServer, '/')
api.add_resource(RegisterClientInstance, '/register_new_client')

if __name__ == "__main__":
    app.run(debug=True, host=sys.argv[1], port=int(sys.argv[2]))
