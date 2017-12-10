#
# Directory server manages the mappings and distribution of files across file-servers.
# It should be able to create new file servers and manage them.
# Files should be given an id from a hash-function, and stored in the table
# This will enable lookups between the incoming requested filename, and the id of the file on the file-servers
# Available at http://127.0.0.1:5000
#
from flask_restful import Resource, Api, request
from flask import Flask
import FileManipAPI as file_api
import requests

CONNECTED_FILESERVERS_BY_ID = {}
FILESERVER_LOAD_BY_ID = {}
FILES_ON_RECORD_BY_NAME = {}
FILES_ON_RECORD_BY_ID = {}
NUM_CLIENTS = 0
VERSION_ZERO = 0

app = Flask(__name__)
api = Api(app)

'''
Common methods used by the directory server resources
'''

def print_to_console(message):
    print ("DirectoryServer: %s" % message)

# This method is used to get the details of the file-server on which the requested filename is stored
def get_server_file_details(file_name, file_names_on_record, connected_fileservers_by_id):
    if file_name in file_names_on_record.keys():
        print_to_console("{0} on record".format(file_name))
        file_id, server_id, file_version = file_names_on_record[str(file_name)]
        server_address = connected_fileservers_by_id[server_id]
        print_to_console("The file {0} is stored on server {1}. The corresponding server address is {2}:{3}".format(file_id, server_id, server_address[0], server_address[1]))
        return server_address, server_id, file_id, file_version
    else:
        print_to_console("File {0} isn't recorded in the directory server.".format(file_name))
        return None, None, None, None

# This method is used to load-balance the file-servers
def find_least_loaded_file_server(connected_fileservers_by_id, file_server_load_by_id):
    server_id = min(file_server_load_by_id, key=file_server_load_by_id.get)
    print_to_console("The least loaded file server is {0}".format(server_id))
    return server_id




class DirectoryServer(Resource):
    '''
    This resource is used by the client library to get and post requests for which fileserver they should communicate with for their files.
    '''

    def get(self):
        file_name =  request.get_json()['file_name']
        print_to_console("Getting {0} mapping ".format(file_name))

        server_address, server_id, file_id, file_version = get_server_file_details(file_name, FILES_ON_RECORD_BY_NAME, CONNECTED_FILESERVERS_BY_ID)
        response = {'file_server_address': server_address, 'file_server_id': server_id, 'file_id': file_id, 'file_version': file_version}
        print_to_console('Response being sent to client: {0}'.format(response))
        return response

    def post(self):
        file_name = request.get_json()['file_name']
        file_contents = request.get_json()['file_contents']
        print_to_console("File {0} requested to post".format(file_name))
        server_address, server_id, file_id, file_version = get_server_file_details(file_name, FILES_ON_RECORD_BY_NAME, CONNECTED_FILESERVERS_BY_ID)

        if file_id is not None:
            # Copy exists on a file-server
            return {'file_server_address': server_address, 'file_server_id': server_id, 'file_id':file_id, 'file_version':file_version, 'new_remote_copy': False}
        else:
            # This is a new file: create a brand new remote copy
            print_to_console("File {0} wasn't found on any server. Will add it least-loaded server.".format(file_name))
            file_id = len(FILES_ON_RECORD_BY_NAME)
            file_server_id = find_least_loaded_file_server(CONNECTED_FILESERVERS_BY_ID, FILESERVER_LOAD_BY_ID)
            FILESERVER_LOAD_BY_ID[file_server_id] += 1

            # add versioning info - initial value
            file_version = VERSION_ZERO
            FILES_ON_RECORD_BY_NAME[file_name] = (file_id, file_server_id, file_version)
            FILES_ON_RECORD_BY_ID[file_id] = (file_server_id, file_name, file_version)
            server_ip = CONNECTED_FILESERVERS_BY_ID[file_server_id][0]
            server_port = CONNECTED_FILESERVERS_BY_ID[file_server_id][1]

            response = requests.post(
                file_api.create_url(server_ip, server_port, 'create_new_remote_copy'),
                json={'file_id': file_id, 'file_contents': file_contents, 'server_id': file_server_id}
            )
            new_remote_copy = response.json()['new_remote_copy']
            if new_remote_copy == True:
                print_to_console("Successfully created remote copy.")

            return {'file_id': file_id, 'file_server_id': file_server_id, 'file_server_address': CONNECTED_FILESERVERS_BY_ID[file_server_id], 'file_version': file_version, 'new_remote_copy': new_remote_copy}


class UpdateFileVersion(Resource):
    '''
    This resource is used by the client library to send an update about the version of the file
    '''

    def post(self):
        file_id = request.get_json()['file_id']
        file_version = request.get_json()['file_version']
        file_server_id = request.get_json()['file_server_id']
        file_name = request.get_json()['file_name']

        # have to check that the file being referenced exists
        if FILES_ON_RECORD_BY_ID[file_id]:
            # now update the version if necessary
            if FILES_ON_RECORD_BY_ID[file_id][2] != file_version:
                if FILES_ON_RECORD_BY_ID[file_id][2] == (file_version - 1):
                    FILES_ON_RECORD_BY_ID[file_id] = {file_server_id, file_name, file_version}
                    print 'Successfully updated version of {0} to version = {1}'.format(file_name, file_version)
                    return {'version_updated': True}
                else:
                    print 'Version of the file {0} is behind that on the directory server'.format(FILES_ON_RECORD_BY_ID[file_id][1])
                    return {'version_updated': False}
            else:
                print 'Version of the file {0} is behind that on the directory server'.format(
                    FILES_ON_RECORD_BY_ID[file_id][1])
                return {'version_updated': False}
        print 'Version of the file {0} is behind that on the directory server'.format(FILES_ON_RECORD_BY_ID[file_id][1])
        return {'version_updated': False}



class RegisterFileserverInstance(Resource):
    '''
    This resource is used by the file-server to register their existence with the directory server.
    The directory server can then work with them to map and store remote copies of files.
    '''

    def post(self):
        global FILESERVER_LOAD_BY_ID

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

        response = {'client_id': client_id}
        print_to_console("NEW CLIENT {0} REGISTERED".format(client_id))
        return response


# this adds a url handle for the Directory Server
api.add_resource(DirectoryServer, '/')
api.add_resource(RegisterFileserverInstance, '/register_fileserver')
api.add_resource(RegisterClientInstance, '/register_client')
api.add_resource(UpdateFileVersion, '/update_file_version')

if __name__ == "__main__":
    # default ip = 127.0.0.1, port = 5000
    app.run(debug=True)
