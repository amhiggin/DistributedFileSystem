#
# Enum to specify the types of operation we want to perform on a file
# Used by the file server to determine what the legitimate requests are.
# Used by the client to be compliant with the request types the server expects.
# Each request type maps to an integer
#

from enum import Enum


class MessageType(Enum):
    def __str__(self):
        return str(self.value)

    # Client request messages
    CHECK_DIR_EXISTS = 0
    CREATE_DIR = 1
    FILE_OPEN = 2
    FILE_READ = 3
    FILE_WRITE = 4
    CREATE_FILE = 5  # implementing
    DELETE_FILE = 6  # not used yet
    CLIENT_ID_REQUEST = 7
    CLIENT_ID_RESPONSE = 8

    # Server response messages
    FILE_EXISTS = 9
    FILE_NOT_EXISTS = 10
    DIR_NOT_FOUND = 11
    # FILE_OPENED? etc

    # Locking service
    LOCk_FILE = 12
    FILE_LOCKED = 13
    UNLOCK_FILE = 14
    FILE_UNLOCKED = 15
    REQUEST_LOCK = 16
    REQUEST_LOCK_DENIED = 17


# THE MINIMUM:
# "CREATE"
# "REMOVE"
# "WRITE"
# "READ"
# "MKDIR"
# "RMDIR"
# "KILL_SERVICE"
# "FILE_EXISTS"
# "DIR_EXISTS"
