#
# Directory server manages the mappings and distribution of files across file-servers.
# It should be able to create new file servers and manage them.
# Files should be given an id from a hash-function, and stored in the table
# This will enable lookups between the incoming requested filename, and the id of the file on the file-servers
# Available at http://127.0.0.1:5000
#
from flask_restful import Resource, Api
from flask import Flask
import DirectoryServerAPI as API

CONNECTED_FILESERVERS_BY_ID = {}
FILESERVER_LOADING = {}
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
    else
        return None, None, None


class DirectoryServer(Resource):

    def get(self, requested_file):
        # TODO look at generating the file_id using a hash function
        server_address, server_id, file_id = get_server_file_details(requested_file)
        return {'file_server_address': server_address, 'file_server_id': server_id, 'file_id': file_id}

    def post(self, requested_file):
        # TODO implement what this does
        return "" # no content to return


# this adds a url handle for the Directory Server
api.add_resource(DirectoryServer, '/')

if __name__ == "__main__":
    app.run(debug=True)
