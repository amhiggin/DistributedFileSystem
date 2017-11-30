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

# TODO look into using a DB to store the key-value pairs?

app = Flask(__name__)
api = Api(app)


class DirectoryServer(Resource):

    def get(self):
        file_name =  request.get_json()['file_name']
        dir_api.print_to_console("File {0} requested to get ".format(file_name))

        server_address, server_id, file_id = dir_api.get_server_file_details(file_name, FILES_ON_RECORD_BY_NAME, CONNECTED_FILESERVERS_BY_ID)
        return {'file_server_address': server_address, 'file_server_id': server_id, 'file_id': file_id}

    def post(self):
        file_name = request.get_json()['file_name']
        file_contents = request.get_json()['file_contents']
        dir_api.print_to_console("File {0} requested to post".format(file_name))
        server_address, server_id, file_id = dir_api.get_server_file_details(file_name, FILES_ON_RECORD_BY_NAME, CONNECTED_FILESERVERS_BY_ID)
        if file_id is not None:
            return {'file_server_address': server_address, 'file_server_id': server_id, 'file_id':file_id, 'new_remote_copy': False}
        else:
            dir_api.print_to_console("File {0} wasn't found on any server. Will add it to a file-server".format(file_name))
            file_id = len(FILES_ON_RECORD_BY_NAME)
            dir_api.print_to_console("Assigned file_id as {0}\nNow will store remote copy on least-loaded file server.".format(file_id))
            file_server_id = dir_api.find_least_loaded_file_server(CONNECTED_FILESERVERS_BY_ID, FILESERVER_LOAD_BY_ID)
            FILESERVER_LOAD_BY_ID[file_server_id] += 1

            FILES_ON_RECORD_BY_NAME[file_name] = (file_id, file_server_id)
            FILES_ON_RECORD_BY_ID[file_id] = (file_server_id, file_name)
            server_ip = CONNECTED_FILESERVERS_BY_ID[file_server_id][0]
            server_port = CONNECTED_FILESERVERS_BY_ID[file_server_id][1]

            response = requests.post(
                file_api.create_url(server_ip, server_port, 'create_new_remote_copy'),
                json={'file_id': file_id, 'file_contents': file_contents, 'server_id': file_server_id}
            )
            new_remote_copy = response.json()['new_remote_copy']
            if new_remote_copy == True:
                dir_api.print_to_console("Successfully created remote copy with requested changes")

            # TODO handle the receipt of the 'success' on the client API side
            return {'file_id': file_id, 'file_server_id': file_server_id, 'file_server_address': CONNECTED_FILESERVERS_BY_ID[file_server_id], 'new_remote_copy': new_remote_copy}


class RegisterFileserverInstance(Resource):

    def post(self):
        global FILESERVER_LOAD_BY_ID
        print "register file server"
        # get server properties
        request_contents = request.get_json()
        server_ip = request_contents['ip']
        print "ip" + server_ip
        server_port = request_contents['port']
        print "port " + server_port
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
        dir_api.print_to_console("NEW CLIENT REGISTERED")
        dir_api.print_to_console("CLIENT ID ASSIGNED AS {0}".format(client_id))
        return response


# this adds a url handle for the Directory Server
api.add_resource(DirectoryServer, '/')
api.add_resource(RegisterFileserverInstance, '/register_fileserver')
api.add_resource(RegisterClientInstance, '/register_client')

if __name__ == "__main__":
    app.run(debug=True)
