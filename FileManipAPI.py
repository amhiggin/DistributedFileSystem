#
# These are methods that can be used between the fileserver and the client.
#


def create_url():
    return "Hello from create_url"


def find_file_if_exists(file_path, file_name):
    return "Hello from find_file_if_exists: " + file_path + file_name