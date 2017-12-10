#
# Directory server manages the mappings and distribution of files across file-servers.
# It should be able to create new file servers and manage them.
# Files should be given an id from a hash-function, and stored in the table
# This will enable lookups between the incoming requested filename, and the id of the file on the file-servers
# Available at http://127.0.0.1:5000
#
from flask_restful import Resource, Api, request
from flask import Flask
import DirectoryServerAPI as dir_api
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


class DirectoryServer(Resource):

    def get(self):
        file_name =  request.get_json()['file_name']
        dir_api.print_to_console("File {0} requested to get ".format(file_name))

        server_address, server_id, file_id, file_version = dir_api.get_server_file_details(file_name, FILES_ON_RECORD_BY_NAME, CONNECTED_FILESERVERS_BY_ID)
        return {'file_server_address': server_address, 'file_server_id': server_id, 'file_id': file_id, 'file_version': file_version}

    def post(self):
        file_name = request.get_json()['file_name']
        file_contents = request.get_json()['file_contents']
        dir_api.print_to_console("File {0} requested to post".format(file_name))
        server_address, server_id, file_id, file_version = dir_api.get_server_file_details(file_name, FILES_ON_RECORD_BY_NAME, CONNECTED_FILESERVERS_BY_ID)

        if file_id is not None:
            # Copy exists on a file-server
            dir_api.print_to_console('Current file version is {0}'.format(file_version))
            return {'file_server_address': server_address, 'file_server_id': server_id, 'file_id':file_id, 'file_version':file_version, 'new_remote_copy': False}
        else:
            # This is a new file: create a brand new remote copy
            dir_api.print_to_console("File {0} wasn't found on any server. Will add it to a file-server".format(file_name))
            file_id = len(FILES_ON_RECORD_BY_NAME)
            dir_api.print_to_console("Assigned file_id as {0}\nNow will store remote copy on least-loaded file server.".format(file_id))
            file_server_id = dir_api.find_least_loaded_file_server(CONNECTED_FILESERVERS_BY_ID, FILESERVER_LOAD_BY_ID)
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
                dir_api.print_to_console("Successfully created remote copy with requested changes")

            return {'file_id': file_id, 'file_server_id': file_server_id, 'file_server_address': CONNECTED_FILESERVERS_BY_ID[file_server_id], 'file_version': file_version, 'new_remote_copy': new_remote_copy}


class UpdateFileVersion(Resource):
    '''
    This resource is used by the client library to send an update about the version of the file
    '''

    def post(self):
        file_id = request.get_json()['file_id']
        file_version = request.get_json()['file_version']
        file_server_id = request.get_json()['file_server_id']

        # have to check that the file being referenced exists
        if FILES_ON_RECORD_BY_ID[file_id]:
            # now update the version if necessary
            if FILES_ON_RECORD_BY_ID[file_id][2] != file_version:
                if FILES_ON_RECORD_BY_ID[file_id][2] == (file_version - 1):
                    FILES_ON_RECORD_BY_ID[file_id][2] = file_version
                    return {'version_updated':True}
                else:
                    print 'Version of the file {0} is behind that on the directory server'.format(FILES_ON_RECORD_BY_ID[file_id][1])
                    return {'version_updated':False}
            else:
                return {'version_updated':False}

        return {'version_updated': False}



class RegisterFileserverInstance(Resource):

    def post(self):
        global FILESERVER_LOAD_BY_ID
        dir_api.print_to_console("register file server")

        # get server properties
        request_contents = request.get_json()
        server_ip = request_contents['ip']
        server_port = request_contents['port']
        server_id = len(CONNECTED_FILESERVERS_BY_ID)

        # make record of file server with directory server
        CONNECTED_FILESERVERS_BY_ID[server_id] = (server_ip, server_port)
        FILESERVER_LOAD_BY_ID[server_id] = 0

        # print
        dir_api.print_to_console("NEW FILESERVER REGISTERED AT: {0}:{1}/".format(server_ip, server_port))
        dir_api.print_to_console("SERVER ID ASSIGNED AS {0}\nFILESERVER {0} READY TO SERVE!".format(server_id))

        # send the id back to the server
        return {'server_id': server_id}


class RegisterClientInstance(Resource):

    def get(self):
        global NUM_CLIENTS
        # we know that the client is just looking for an id
        client_id = NUM_CLIENTS
        NUM_CLIENTS += 1
        response = {'client_id': client_id}
        dir_api.print_to_console("NEW CLIENT REGISTERED. CLIENT ID ASSIGNED AS {0}".format(client_id))
        return response


# this adds a url handle for the Directory Server
api.add_resource(DirectoryServer, '/')
api.add_resource(RegisterFileserverInstance, '/register_fileserver')
api.add_resource(RegisterClientInstance, '/register_client')
# The following should allow the fileserver to send an update to the dir server about a changed file version
api.add_resource(UpdateFileVersion, '/update_file_version')

if __name__ == "__main__":
    app.run(debug=True)
