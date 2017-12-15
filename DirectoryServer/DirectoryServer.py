#
# Directory server manages the mappings and distribution of files across file-servers.
# It should be able to create new file servers and manage them.
# Files should be given an id from a hash-function, and stored in the table
# This will enable lookups between the incoming requested filename, and the id of the file on the file-servers
# Available at http://127.0.0.1:5000
#
import os
from flask_restful import Resource, Api, request
from flask import Flask
import requests, sys
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import FileManipAPI as file_api

CONNECTED_FILESERVERS_BY_ID = {}
FILESERVER_LOAD_BY_ID = {}
FILES_ON_RECORD_BY_NAME = {}
FILES_ON_RECORD_BY_ID = {}
NUM_CLIENTS = 0
VERSION_ZERO = 0

app = Flask(__name__)
api = Api(app)


'''                  '''
''' COMMON FUNCTIONS '''
'''                  '''

def print_to_console(message):
    print ("DirectoryServer: %s" % message)


def create_new_remote_copy(file_name, file_contents):
    # Determine the id, least-loaded server, that server's address details.
    file_id = len(FILES_ON_RECORD_BY_NAME)
    file_server_id = find_least_loaded_file_server(CONNECTED_FILESERVERS_BY_ID, FILESERVER_LOAD_BY_ID)

    if file_server_id is -1:
        # There are no registered file-servers: send back 'None' server id as a remote copy cannot be created.
        return {'file_id': file_id, 'file_server_id': None, 'file_server_address': None, 'file_version': None,
                'new_remote_copy': None}

    # Update the directory server records.
    FILESERVER_LOAD_BY_ID[file_server_id] += 1
    FILES_ON_RECORD_BY_NAME[file_name] = (file_id, file_server_id, VERSION_ZERO)
    FILES_ON_RECORD_BY_ID[file_id] = (file_server_id, file_name, VERSION_ZERO)

    # Get the address details for the file-server on which the remote copy is stored
    server_ip = CONNECTED_FILESERVERS_BY_ID[file_server_id][0]
    server_port = CONNECTED_FILESERVERS_BY_ID[file_server_id][1]

    # Create the new remote copy of this file directly (no action required from client).
    response = requests.post(
        file_api.create_url(server_ip, server_port, 'create_new_remote_copy'),
        json={'file_id': file_id, 'file_contents': file_contents, 'server_id': file_server_id}
    )
    new_remote_copy = response.json()['new_remote_copy']
    if new_remote_copy == True:
        print_to_console("Successfully created remote copy.")

    return {'file_id': file_id, 'file_server_id': file_server_id,
            'file_server_address': CONNECTED_FILESERVERS_BY_ID[file_server_id], 'file_version': VERSION_ZERO,
            'new_remote_copy': new_remote_copy}

def update_version_of_file_in_mapping(file_id, file_server_id, file_version, file_name):
    # have to check that the file being referenced has an existing record
    if FILES_ON_RECORD_BY_ID[file_id]:

        # now update the version if necessary
        if FILES_ON_RECORD_BY_ID[file_id][2] is not file_version:

            if FILES_ON_RECORD_BY_ID[file_id][2] is (file_version - 1):
                FILES_ON_RECORD_BY_ID[file_id] = (file_server_id, file_name, file_version)
                FILES_ON_RECORD_BY_NAME[file_name] = (file_id, file_server_id, file_version)
                print 'Successfully updated version of {0} to version = {1}'.format(file_name, file_version)
                return {'version_updated': True}
            else:
                print 'Version of the file {0} is behind that on the directory server'.format(
                    FILES_ON_RECORD_BY_ID[file_id][1])
                return {'version_updated': False}
        else:
            print_to_console("The version hasn't changed since the last update. Was {0}, is now {1}..".format(
                FILES_ON_RECORD_BY_ID[file_id][2], file_version))
            return {'version_updated': False}
    else:
        print 'There is no remote copy of file {0} recorded with the directory server'.format(
            FILES_ON_RECORD_BY_ID[file_id][1])
        return {'version_updated': False}

# This method is used to get the details of the file-server on which the requested filename is stored
def get_server_file_details(file_name, file_names_on_record, connected_fileservers_by_id):
    if file_name in file_names_on_record.keys():
        print_to_console("{0} on record".format(file_name))
        file_id, server_id, file_version = file_names_on_record[str(file_name)]
        server_address = connected_fileservers_by_id[server_id]
        print_to_console("The file {0} (with version {1}) is stored on file-server {2}. The corresponding server address is {3}:{4}".format(file_id, file_version, server_id, server_address[0], server_address[1]))
        return server_address, server_id, file_id, file_version
    else:
        print_to_console("File {0} isn't recorded in the directory server.".format(file_name))
        return None, None, None, None

# This method is used to load-balance the file-servers.
def find_least_loaded_file_server(connected_fileservers_by_id, file_server_load_by_id):
    if len(connected_fileservers_by_id) is 0 or len(file_server_load_by_id) is 0:
        print_to_console("There are no file-servers registered - cannot service the load balance request.")
        return -1
    server_id = min(file_server_load_by_id, key=file_server_load_by_id.get)
    print_to_console("The least loaded file server is {0}.".format(server_id))
    return server_id


'''                      '''
''' RESOURCE DEFINITIONS '''
'''                      '''

class DirectoryServer(Resource):
    '''
    This resource is used by the client library to get and post requests for which fileserver they should communicate with for their files.
    '''

    def get(self):
        file_name =  request.get_json()['file_name']
        print_to_console("Request to get {0} file mapping.".format(file_name))

        server_address, server_id, file_id, file_version = get_server_file_details(file_name, FILES_ON_RECORD_BY_NAME, CONNECTED_FILESERVERS_BY_ID)
        response = {'file_server_address': server_address, 'file_server_id': server_id, 'file_id': file_id, 'file_version': file_version}
        return response

    def post(self):
        file_name = request.get_json()['file_name']
        file_contents = request.get_json()['file_contents']
        print_to_console("Request to post file {0} and return mapping.".format(file_name))
        server_address, server_id, file_id, file_version = get_server_file_details(file_name, FILES_ON_RECORD_BY_NAME, CONNECTED_FILESERVERS_BY_ID)

        if file_id is not None:
            # A remote copy exists on a file-server: return the details to the client
            print_to_console("A remote copy of {0} with version {1}, exists.".format(file_name, file_version))
            return {'file_server_address': server_address, 'file_server_id': server_id, 'file_id':file_id, 'file_version':file_version, 'new_remote_copy': False}
        else:
            # This is a new file with no existing remote copy: create one on the least-loaded server.
            print_to_console("Remote copy of file {0} wasn't found on any server. Will create a remote copy on the least-loaded server.".format(file_name))
            response = create_new_remote_copy(file_name, file_contents)
            return response



class UpdateFileVersion(Resource):
    '''
    This resource is used by the client library to send an update about the version of the file
    '''

    def post(self):
        file_id = request.get_json()['file_id']
        file_version = request.get_json()['file_version']
        file_server_id = request.get_json()['file_server_id']
        file_name = request.get_json()['file_name']

        # Determine the correct response depending on the difference between incoming and previous versions.
        response = update_version_of_file_in_mapping(file_id, file_server_id, file_version, file_name)
        return response



class RegisterFileserverInstance(Resource):
    '''
    This resource is used by the file-server to register their existence with the directory server.
    The directory server can then work with them to map and store remote copies of files.
    '''

    def post(self):
        # get server properties
        request_contents = request.get_json()
        server_ip = request_contents['ip']
        server_port = request_contents['port']
        server_id = len(CONNECTED_FILESERVERS_BY_ID)

        # make record of file server with directory server
        CONNECTED_FILESERVERS_BY_ID[server_id] = (server_ip, server_port)
        FILESERVER_LOAD_BY_ID[server_id] = 0

        print_to_console("NEW FILE SERVER REGISTERED AT: {0}:{1}/ WITH ID {2}".format(server_ip, server_port, server_id))

        # send the id back to the server
        return {'server_id': server_id}


class RegisterClientInstance(Resource):
    '''
    This resource is used by the client API to register the client with the directory server.
    The directory server can then work with them to map and store remote copies of the files that the clients want to persist.
    '''
    def get(self):
        # we know that the client is just looking for an id
        global NUM_CLIENTS

        client_id = NUM_CLIENTS
        NUM_CLIENTS += 1

        print_to_console("NEW CLIENT {0} REGISTERED".format(client_id))

        response = {'client_id': client_id}
        return response


# this adds a url handle for the Directory Server
api.add_resource(DirectoryServer, '/')
api.add_resource(RegisterFileserverInstance, '/register_fileserver')
api.add_resource(RegisterClientInstance, '/register_client')
api.add_resource(UpdateFileVersion, '/update_file_version')

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

