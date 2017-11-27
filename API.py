#
# This is the library of function calls that the client will be able to use.
# It should allow for read, write, etc. (possibly locking also).
#

import os, sys
import flask
import flask_restful
import requests
import FileManipAPI as FILE_API


def run():
    print "in run"


# download a copy of the file
# should inform lock server of the fact that it has a copy
def read_file(file_path, file_name):
    print "Request to read " + file_path

    # get whatever is available on fileserver URL
    response = requests.get("http://127.0.0.1:45678")
    print "response: " + response.json()['Hello']


# upload a changed copy of the file
# should inform the lock server of the fact that it is updating a copy
def write_file(file_path, file_name):
    print "Request to write " + file_path
    # NOT implemented yet
    return 0


# check the file exists on the fileserver, as such
def open_file(file_path, file_name):
    print "Request to open " + file_path
    # NOT implemented yet


# doesn't really do anything effective (from what I can see)
def close_file(file_path, file_name):
    print "Request to close " + file_path
    # NOT implemented yet


def main():
    return 0


if __name__ == "__main__":
    run()