#
# These are methods that can be used between the fileserver and the client.
#
import os

# Directory server started at default Flask address for ease
DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)
LOCKING_SERVER_ADDRESS = ("127.0.0.1", 5001)

def create_root_dir_if_not_exists(root_path):
    if not os.path.exists(root_path):
        os.mkdir(root_path)


# create a url to query
def create_url(ip, port, endpoint):
    url = "http://{0}:{1}/{2}".format(ip, port, endpoint)
    return url


# gets a name for the file, equal to the file id
def get_serverside_file_name_by_id(file_id):
    return str(file_id) + '.txt'

