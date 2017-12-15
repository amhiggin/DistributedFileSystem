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


'''                  '''
''' COMMON FUNCTIONS '''
'''                  '''

# Print a message to the console, labelled with the locking server's details.
def print_to_console(message):
    print ("LockingServer: %s" % message)


# This method is a safety mechanism, such that if a client with a write lock on a file dies, the file will not be infinitely locked.
def timeout_on_lock(file_id):
    locked_time = LOCKED_FILES_BY_ID[file_id]['timestamp']
    current_time = datetime.datetime.now()
    difference = current_time - locked_time
    if difference >= datetime.timedelta(seconds=TIMEOUT):
        return True
    else:
        return False


'''                      '''
''' RESOURCE DEFINITIONS '''
'''                      '''


class LockingServer(Resource):

    # This method deals with requests to acquire a lock.
    def put(self):
        # get request contents
        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']

        # validate the request
        if client_id not in REGISTERED_CLIENTS_BY_ID.keys():
            print_to_console("Client {0} is not registered with the locking server! Can't place a lock on {1}.".format(client_id, file_id))
            return {'locked': None}

        # Get the current time - used to check whether the timeout has occurred for a lock, if appropriate.
        current_time = datetime.datetime.now()

        if file_id in LOCKED_FILES_BY_ID:
            # This file is recorded on the locking server
            if LOCKED_FILES_BY_ID[file_id]['locked'] == True:
                # The file is currently locked
                if timeout_on_lock(file_id):
                    # The lock has not been released in the past 60 seconds - force release it (assume client died).
                    print_to_console("Timeout reached on file {0}: unlocking".format(file_id))
                    LOCKED_FILES_BY_ID[file_id] = {'locked': False, 'timestamp': None, 'client_id': None}

            if LOCKED_FILES_BY_ID[file_id]['locked'] is False or LOCKED_FILES_BY_ID[file_id]['locked'] is None:
                # The file isn't locked: acquire it
                LOCKED_FILES_BY_ID[file_id] = {'locked': True, 'timestamp': current_time, 'client_id':client_id}
                print_to_console('Client {0} has successfully locked file {1}'.format(client_id, file_id))
                return{'locked': True}
            else:
                # The file is locked: reject request.
                print_to_console("Client {0} couldn't lock file {1}".format(client_id, file_id))
                return {'locked': False}
        else:
            # This file isn't recorded as ever having been locked: we can lock it!
            LOCKED_FILES_BY_ID[file_id] = {'locked': True, 'timestamp': current_time, 'client_id':client_id}
            print_to_console('Client {0} has successfully locked file {1}'.format(client_id, file_id))
            return {'locked': True}

    # This method deals with requests to release a lock.
    def delete(self):
        # extract file details
        file_id = request.get_json()['file_id']
        client_id = request.get_json()['client_id']

        # validate the request
        if client_id not in REGISTERED_CLIENTS_BY_ID.keys():
            print_to_console("Client {0} is not registered with the locking server! Can't release any locks!".format(client_id))
            return {'locked': None}

        if file_id in LOCKED_FILES_BY_ID.keys():
            # This file is recorded with the locking server
            if LOCKED_FILES_BY_ID[file_id]['locked'] == True and LOCKED_FILES_BY_ID[file_id]['client_id'] is client_id:
                # We have the lock: so we can now release the lock.
                LOCKED_FILES_BY_ID[file_id]['locked'] = False
                print_to_console('Client {0} has unlocked file {1}'.format(client_id, file_id))
                return {'locked': False}
            else:
                # We can't unlock the file - either it isn't locked, or we aren't the one who locked it.
                return {'locked': LOCKED_FILES_BY_ID[file_id]['locked']}
        # in either case, we return that the file is unlocked
        else:
            if LOCKED_FILES_BY_ID[file_id]['client_id'] is not client_id:
                print_to_console("Client {0} never locked the file: can't unlock it!".format(client_id))
                return {'locked': None}
            else:
                print_to_console('File {0} was never locked!'.format(file_id))
                return {'locked': False}

    # Used to handle requests to check whether a file is locked.
    def get(self):
        # extract file details
        file_id = request.get_json()['file_id']

        if file_id in LOCKED_FILES_BY_ID:
            # a record of this file exists with the locking server
            if LOCKED_FILES_BY_ID[file_id]['locked'] is True:
                print_to_console('File {0} is locked'.format(file_id))
                return {'locked': True}
            else:
                print_to_console('File {0} is not locked'.format(file_id))
                return {'locked':False}
        # The file doesn't have any record with the locking server - thus isn't locked.
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
    try:
        if len(sys.argv) == 3:
            app.run(debug=True, host=sys.argv[1], port=int(sys.argv[2]))
        else:
            print_to_console("IP address and port weren't entered correctly for the locking server: cannot launch.")
        exit(0)
    except Exception as e:
        print_to_console("An error occurred when trying to launch using params {0}:{1}. Error message: {2}".format(sys.argv[1], sys.argv[2], e.message))
        exit(0)