#
# Directory server manages the mappings and distribution of files across file-servers.
# It should be able to create new file servers and manage them.
# Files should be given an id from a hash-function, and stored in the table
# This will enable lookups between the incoming requested filename, and the id of the file on the file-servers
# Available at http://127.0.0.1:5000
#
from flask_restful import Resource, Api, request
from flask import Flask
import DirectoryServerAPI as API

CONNECTED_FILESERVERS_BY_ID = {}
FILESERVER_LOAD = {}
FILE_NAMES_ON_RECORD = {}

# TODO look into using a DB to store the key-value pairs?

app = Flask(__name__)
api = Api(app)


def print_to_console(message):
    print ("DirectoryServer: %s%s" % (message, '\n'))


def get_server_file_details(file_name):
    if file_name in FILE_NAMES_ON_RECORD.keys():
        print "{0} on record - now will have to find where it is".format(file_name)
        file_id, server_id = FILE_NAMES_ON_RECORD[str(file_name)]
        server_address = CONNECTED_FILESERVERS_BY_ID[server_id]
        return server_address, server_id, file_id
    else:
        return None, None, None


class DirectoryServer(Resource):

    def get(self, requested_file):
        print_to_console("File {0} requested to get".format(requested_file))
        # TODO look at generating the file_id using a hash function
        server_address, server_id, file_id = get_server_file_details(requested_file)
        return {'file_server_address': server_address, 'file_server_id': server_id, 'file_id': file_id}

    def post(self, requested_file):
        # TODO implement what this does
        print_to_console("File {0} requested to post".format(requested_file))
        server_address, server_id, file_id = get_server_file_details(requested_file)
        if requested_file in FILE_NAMES_ON_RECORD:
            return {'file_server_address': server_address, 'file_server_id': server_id, 'file_id':file_id}
        else:
            # TODO handle this on client side
            return None, None, None


class RegisterFileserverInstance(Resource):

    def post(self):
        global FILESERVER_LOAD
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
        FILESERVER_LOAD[server_id] = 0

        # print
        print_to_console("NEW FILESERVER REGISTERED AT: {0}:{1}/".format(server_ip, server_port))
        print_to_console("SERVER ID ASSIGNED AS {0}\nFILESERVER {0} READY TO SERVE!".format(server_id))

# this adds a url handle for the Directory Server
api.add_resource(DirectoryServer, '/')
api.add_resource(RegisterFileserverInstance, '/register_fileserver')

if __name__ == "__main__":
    app.run(debug=True)
