#
# This is the library of function calls that the client will be able to use.
# It should allow for read, write, etc. (possibly locking also).
#

import os, sys
import flask
import flask_restful


# download a copy of the file
# should inform lock server of the fact that it has a copy
def read_file(file_path):
    print "Request to read " + file_path


# upload a changed copy of the file
# should inform the lock server of the fact that it is updating a copy
def write_file(file_path):
    print "Request to write " + file_path


# check the file exists on the fileserver, as such
def open_file(file_path):
    print "Request to open " + file_path


# doesn't really do anything effective (from what I can see)
def close_file(file_path):
    print "Request to close " + file_path