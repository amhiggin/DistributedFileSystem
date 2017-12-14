#
# These are methods that can be used between the fileserver and the client.
#
import os

DIRECTORY_SERVER_ADDRESS = ("127.0.0.1", 5000)
LOCKING_SERVER_ADDRESS = ("127.0.0.1", 5001)


# Creates a new root directory if one does not already exist.
def create_root_dir_if_not_exists(root_path):
    if not os.path.exists(root_path):
        os.mkdir(root_path)


# Construct a full url given the hostname, port and endpoint.
def create_url(ip, port, endpoint):
    url = "http://{0}:{1}/{2}".format(ip, port, endpoint)
    return url


# Constructs a .txt filename, given the file identifier.
def get_serverside_file_name_by_id(file_id):
    return str(file_id) + '.txt'

