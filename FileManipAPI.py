#
# These are methods that can be used between the fileserver and the client.
# TODO populate
#

import os


def create_root_dir_if_not_exists(root_path):
    if not os.path.exists(root_path):
        os.mkdir(root_path)


# create a url to query
def create_url(ip, port):
    return "http://{0}:{1}".format(ip, port)
